from odoo import models, fields, api,exceptions, _
from odoo.tools.misc import xlwt
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

    def action_validate1(self):
        if self.state == 'to_approve':
            self.state = 'second_approval'
            self.action_send_email()

    def action_validate2(self):
        if self.state == 'second_approval':
            self.state = 'approved'
            self.action_send_email()

    def action_refuse1(self):
        if self.state in ['to_approve', 'second_approval']:
            self.state = 'rejected'
            self.action_send_email()

    def action_refuse2(self):
        if self.state in ['to_approve', 'second_approval']:
            self.state = 'rejected'
            self.action_send_email()

    
    def create(self,vals):
        if vals.get('request_number', _('New'))== _('New'):
            vals['request_number'] = self.env['ir.sequence'].next_by_code('request.number') or _('New')
            vals['state']='to_approve'
        res = super(RequestForm, self).create(vals)
        return res
    
    @api.model
    # personalizing user data
    def _get_my_records(self):
        return self.search([('create_uid', '=', self.env.uid)])
    
    def _search(self, args, offset=0, limit=None, order=None, access_rights_uid=None):
        if not access_rights_uid:
            access_rights_uid = self.env.uid
        if not self.env.is_admin()and not (self.env.user.has_group('RequestForm.group_my_custom_group') or self.env.user.has_group('RequestForm.group_custom_group')):
            args += [('create_uid', '=', self.env.uid)]
        return super(RequestForm, self)._search(args, offset=offset, limit=limit, order=order, access_rights_uid=access_rights_uid)
    
    # sending email
    def action_send_email(self):
        template = self.env.ref('RequestForm.email_template_approval_status')
        for rec in self:
            template.send_mail(rec.id, force_send=True)
        else:
            _logger.warning("Email ID is not set for record ID: %s" % rec.id)
        return True


        