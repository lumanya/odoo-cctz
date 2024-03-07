from odoo import models, fields, api,exceptions, _
from odoo.tools.misc import xlwt
from odoo import http
import werkzeug.urls
from odoo.http import request
from werkzeug.urls import url_encode
from odoo.http import request
from odoo.tools import email_split
from odoo.exceptions import UserError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import logging

_logger = logging.getLogger(__name__)

counter = 0

class RequestForm(models.Model):
    _name = 'request.form'
    _inherit = 'mail.thread'
    _description = 'A form of change request'

    submitter_name_id = fields.Many2one('res.users',string='Submitter Name', required=True, default=lambda self: self.env.user, readonly=True)

    cr_Type = fields.Selection(
        string='Type of CR',
        selection=[('enhancement', 'Enhancement'), ('defects', 'Defects')],
        default='enhancement',
        required=True
    )

    description_request = fields.Text(string='Brief description of Request')

    date_submitted = fields.Date(string="Date Submitted", default=lambda self: fields.Date.today(), required=True)

    date_required = fields.Date(string="Date Required", required=True)

    priority = fields.Selection(
        string='Priority',
        selection=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('mandatory', 'Mandatory')],
        default='low',
        required=True
    )

    team_assigned_id = fields.Many2one('res.users', string='Team / Individual assigned to carry out change', required=True)

    reason_for_change = fields.Text(string='Reason for change', required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('second_approval', 'Second Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', required=True, tracking=True)

    active = fields.Boolean(default=True, readonly=True)


    risk = fields.Selection([
        ('high', 'High'),
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('no_risk', 'No Risk'),
    ], string='Risk Level', default='no_risk', required=True)

    department_impacted_id = fields.Many2one('hr.department', string='Department Impacted', required=True)

    impacts_effects = fields.Text(string='What is the Impacts/Effects', required=True)

    additional_instructions = fields.Text(string='Additional Instructions')

    fall_back = fields.Text(string='Fall Back Plan', required=True)

    request_number = fields.Char(string='Change Request Number', copy=False, readonly=True, required=True, default=lambda self: _('New'))

    _rec_name = 'request_number'

    def action_validate1(self):
        if self.state == 'to_approve':
            self.state = 'second_approval'
            self.action_send_email()
            self.send_email_to_second_approvers()
        return True

    def action_validate2(self):
        if self.state == 'second_approval':
            self.state = 'approved'
            self.action_send_email()
            self.action_send_email_assigned()
            

    def action_refuse1(self):
        if self.state in ['to_approve', 'second_approval']:
            self.state = 'rejected'
            self.action_send_email()
            self.action_send_email_assigned()

    def action_refuse2(self):
        if self.state in ['to_approve', 'second_approval']:
            self.state = 'rejected'
            self.action_send_email()

    @api.model
    def create(self, vals):
        if vals.get('request_number', _('New'))== _('New'):
            vals['request_number'] = self.env['ir.sequence'].next_by_code('request.number') or _('New')
            vals['state']='to_approve'
        res = super(RequestForm, self).create(vals)
        res.send_email_to_first_approvers()
        return res
    

    
    @api.model
    # personalizing user data
    def _get_my_records(self):
        return self.search([('create_uid', '=', self.env.uid)])
   
    # sending email
    def action_send_email(self):
        template = self.env.ref('cctz_request_form.email_template_approval_status')
        for rec in self:
            template.send_mail(rec.id, force_send=True)
        


    def action_send_email_assigned(self):
        template1 = self.env.ref('cctz_request_form.assigned_change_template')
        for rec in self:
            template1.send_mail(rec.id, force_send=True)
        else:
            _logger.warning("Email ID is not set for record ID: %s" % rec.id)
        return True  
    
    def _get_second_approvers_emails(self):
        group = self.env.ref('cctz_request_form.group_custom_group')
        users = group.users
        return [user for user in users if user.email]
    
    def send_email_to_second_approvers(self):
        group = self.env.ref('cctz_request_form.group_custom_group')
        users = group.users
        template = self.env.ref('cctz_request_form.email_template_second_approver')
        
        if template and users:
            for user in users:
                if user.email:
                    template.with_context(user=user).send_mail(self.id, force_send=True, email_values={'email_to': user.email})
                    _logger.info("Email sent to %s (%s)" % (user.name, user.email))
                else:
                    _logger.warning("User %s does not have an email address." % user.name)
        else:
            if not template:
                _logger.warning("Email template 'email_template_second_approver' not found.")
            if not users:
                _logger.warning("No users found in the 'Second Approvers' group.")

    def _get_first_approvers_emails(self):
        group = self.env.ref('cctz_request_form.group_my_custom_group')
        users = group.users
        return [user for user in users if user.email]
    
    def send_email_to_first_approvers(self):
        group = self.env.ref('cctz_request_form.group_my_custom_group')
        users = group.users
        template = self.env.ref('cctz_request_form.email_template_first_approver')
        
        if template and users:
            for user in users:
                if user.email:
                    template.with_context(user=user).send_mail(self.id, force_send=True, email_values={'email_to': user.email})
                    _logger.info("Email sent to %s (%s)" % (user.name, user.email))
                else:
                    _logger.warning("User %s does not have an email address." % user.name)
        else:
            if not template:
                _logger.warning("Email template 'email_template_first_approver' not found.")
            if not users:
                _logger.warning("No users found in the 'First Approvers' group.")


    menu_id = fields.Integer(string='Menu ID')
    action_id = fields.Integer(string='Action ID')


    
    @api.model
    def generate_link(self, menu_id, action_id):
        
        base_url = request.httprequest.url_root
        
        # Find menu_id based on the menu name
        menu = self.env['ir.ui.menu'].search([('name', '=', 'My Requests')])
        menu_id = menu.id if menu else False
        
        # Find action_id based on the action name
        action = self.env['ir.actions.act_window'].sudo().search([('name', '=', 'My Change Requests')])
        action_id = action.id if action else False
        
        if menu_id and action_id:
            params = {'menu_id': menu_id, 'action': action_id}
            return base_url + '/web#' + url_encode(params)
        else:
            # Handle the case where either menu or action is not found
            return False
        

    menu_id = fields.Integer(string='Menu ID')
    action_id = fields.Integer(string='Action ID')


    @api.model
    def generate_manage_link(self, menu_id, action_id):
        base_url = request.httprequest.url_root

        # Check if the current user is an admin
        is_admin = self.env.user.has_group('base.group_system')

        # If user is admin, use the specified menu and action IDs
        if is_admin:
            menu_id = self.env.ref('cctz_request_form.menu_manage').id
            action_id = self.env.ref('cctz_request_form.action_manage_view').id
        else:
            # If user is not admin, use the specified menu and action IDs for normal users
            menu_id = self.env.ref('cctz_request_form.menu_manage').id
            action_id = self.env.ref('cctz_request_form.action_manage_view').id

        if menu_id and action_id:
            params = {'menu_id': menu_id, 'action': action_id}
            return base_url + '/web#' + url_encode(params)
        else:
            return False
