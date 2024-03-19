from odoo import models, fields, api,_
from odoo.exceptions import UserError
from odoo.http import request
from werkzeug.urls import url_encode
import logging

_logger = logging.getLogger(__name__)

class loanform(models.Model):
    _name = 'loan.form'
    _inherit='mail.thread'
    _description = 'A loan Form'

    b_state = fields.Selection([
        ('on', 'on'),
        ('off', 'off'),
        ], default='off')


    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('second_approval', 'Second Approval'),
        ('third_approval', 'Third Approval'),
        ('approved', 'Approved'),
        ('rejected','Rejected')
        ], string='Status', default='draft', track_visibility='onchange', tracking=True)

    active = fields.Boolean(default=True, readonly=True)

    loan_amount = fields.Integer(string='Loan amount', required=True)
    repayment_months = fields.Selection(
    string='Repayment months',
    selection=[
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12')
    ],
    default='1',
    )
    reason = fields.Text(string='Reason', required=True)
    constant = fields.Float(default=0.01)
    constant1 = fields.Float(default=0.005)

    service_charge = fields.Float(string='service charge', compute= '_calculate_service_charge')
    subtotal = fields.Float(string='subtotal', compute='_calculate_subtotal')
    monthly_rate=fields.Float(string='Monthly Rate', compute='_calculate_monthly_rate')
    monthly_interest=fields.Float(string='Monthly Interest', compute='_calculate_monthly_interest')
    total_loan=fields.Float(string='Total Loan', compute='_calculate_Total')

    loan_form_number = fields.Char(string='Loan Form Number', copy=False, readonly=True, required=True, default=lambda self: _('New'))

    attachment_ids = fields.One2many('ir.attachment', 'res_id', string="Attachments", required=True)
   
    supported_attachment_ids = fields.Many2many(
        'ir.attachment', string="Attach File", compute='_compute_supported_attachment_ids',
        inverse='_inverse_supported_attachment_ids', required=True)
    supported_attachment_ids_count = fields.Integer(compute='_compute_supported_attachment_ids', required=True)

    repayment_schedule = fields.Text(string="Avarage Monthly Return", compute='_compute_repayment_schedule')

    _rec_name = 'loan_form_number'

    
    @api.model
    def create(self, vals):
        vals['b_state'] = 'on'
        if vals.get('loan_form_number', _('New'))== _('New'):
            vals['loan_form_number'] = self.env['ir.sequence'].next_by_code('loan.number') or _('New')
        res = super(loanform, self).create(vals)
        return res
    
    @api.depends('attachment_ids')
    def _compute_supported_attachment_ids(self):
        for record in self:
            record.supported_attachment_ids = record.attachment_ids
            record.supported_attachment_ids_count = len(record.attachment_ids.ids)

    def _inverse_supported_attachment_ids(self):
        for record in self:
            record.attachment_ids = record.supported_attachment_ids

    @api.depends('loan_amount', 'constant')
    def _calculate_service_charge(self):
        for record in self:
            record.service_charge = record.loan_amount * record.constant

    @api.depends('loan_amount', 'service_charge')
    def _calculate_subtotal(self):
        for record in self:
            record.subtotal = record.loan_amount + record.service_charge

    @api.depends('constant1', 'repayment_months')
    def _calculate_monthly_rate(self):
        for record in self:
            record.monthly_rate = record.constant1 * int(record.repayment_months)

    @api.depends('monthly_rate', 'subtotal')
    def _calculate_monthly_interest(self):
        for record in self:
            record.monthly_interest = record.monthly_rate * record.subtotal

    @api.depends('subtotal', 'monthly_interest')
    def _calculate_Total(self):
        for record in self:
            record.total_loan = record.subtotal + record.monthly_interest

    @api.depends('total_loan', 'repayment_months')
    def _compute_repayment_schedule(self):
        for record in self:
            record.repayment_schedule = record.total_loan / int(record.repayment_months)

    

    def action_submit(self):
        if self.env.user.employee_id and self.env.user.employee_id.loan_officer_id:
            group_officer1 = self.env.ref('loan_form.loan_officer_group')
            group_officer1.write({'users': [(4, self.env.user.employee_id.loan_officer_id.id)]})

            accountant = self.env['hr.employee'].search([('job_title', '=', 'Head of Procurement & Accountant')], limit=1)
            group_officer2 = self.env.ref('loan_form.accountant_group') 
            group_officer2.write({'users': [(4, accountant.user_id.id)]})

            general_manager = self.env['hr.employee'].search([('job_title', '=', 'General Manager')], limit=1)
            group_officer3 = self.env.ref('loan_form.general_manager_group') 
            group_officer3.write({'users': [(4, general_manager.user_id.id)]})
            self.state = 'to_approve'
            self.send_email_to_loan_officer()
        else:
            raise UserError("Please contact your Administrator to set your Loan Officer.")

        
    def action_approve(self):
        self.state = 'second_approval'
        self.action_send_email()
        self.send_email_to_accountant()

    def action_reject(self):
        self.state = 'rejected'
        self.action_send_email()

    def action_approve1(self):
        self.state = 'third_approval'
        self.action_send_email()
        self.send_email_to_general_manager()

    def action_reject1(self):
        self.state = 'rejected'
        self.action_send_email()


    def action_approve2(self):
        self.state = 'approved'
        self.action_send_email()

    def action_reject2(self):
        self.state = 'rejected'
        self.action_send_email()

    menu_id = fields.Integer(string='Menu ID')
    action_id = fields.Integer(string='Action ID')


    
    @api.model
    def generate_link(self, menu_id, action_id):
        
        base_url = request.httprequest.url_root
        
        # Find menu_id based on the menu name
        menu = self.env['ir.ui.menu'].search([('name', '=', 'My Loans')])
        menu_id = menu.id if menu else False
        
        # Find action_id based on the action name
        action = self.env['ir.actions.act_window'].sudo().search([('name', '=', 'Loan Request')])
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
            menu_id = self.env.ref('loan_form.menu_loan_requests').id
            action_id = self.env.ref('loan_form.action_loan_view').id
        else:
            # If user is not admin, use the specified menu and action IDs for normal users
            menu_id = self.env.ref('loan_form.menu_loan_requests').id
            action_id = self.env.ref('loan_form.action_loan_view').id

        if menu_id and action_id:
            params = {'menu_id': menu_id, 'action': action_id}
            return base_url + '/web#' + url_encode(params)
        else:
            return False

        

    def _get_my_records(self):
        return self.search([('create_uid', '=', self.env.uid)])
   
    # sending email
    def action_send_email(self):
        template = self.env.ref('loan_form.email_loan_approval_status')
        for rec in self:
            template.send_mail(rec.id, force_send=True)

    
    def _get_loan_officer_emails(self):
        group = self.env.ref('loan_form.loan_officer_group')
        users = group.users
        return [user for user in users if user.email]
    
    def send_email_to_loan_officer(self):
        group = self.env.ref('loan_form.loan_officer_group')
        users = group.users
        template = self.env.ref('loan_form.email_template_loan_officer_approver')
        
        if template and users:
            for user in users:
                if user.email:
                    template.with_context(user=user).send_mail(self.id, force_send=True, email_values={'email_to': user.email})
                    _logger.info("Email sent to %s (%s)" % (user.name, user.email))
                else:
                    _logger.warning("User %s does not have an email address." % user.name)
        else:
            if not template:
                _logger.warning("Email template 'email_template_loan_officer_approver' not found.")
            if not users:
                _logger.warning("No users found in the 'Loan Officers' group.")

    
    def _get_accountant_emails(self):
        group = self.env.ref('loan_form.accountant_group')
        users = group.users
        return [user for user in users if user.email]
    
    def send_email_to_accountant(self):
        group = self.env.ref('loan_form.accountant_group')
        users = group.users
        template = self.env.ref('loan_form.email_template_accountant_approver')
        
        if template and users:
            for user in users:
                if user.email:
                    template.with_context(user=user).send_mail(self.id, force_send=True, email_values={'email_to': user.email})
                    _logger.info("Email sent to %s (%s)" % (user.name, user.email))
                else:
                    _logger.warning("User %s does not have an email address." % user.name)
        else:
            if not template:
                _logger.warning("Email template 'email_template_accountant_approver' not found.")
            if not users:
                _logger.warning("No users found in the 'Accountant' group.")


    def _get_general_manager_emails(self):
        group = self.env.ref('loan_form.general_manager_group')
        users = group.users
        return [user for user in users if user.email]
    
    def send_email_to_general_manager(self):
        group = self.env.ref('oan_form.general_manager_group')
        users = group.users
        template = self.env.ref('loan_form.email_template_general_manager_approver')
        
        if template and users:
            for user in users:
                if user.email:
                    template.with_context(user=user).send_mail(self.id, force_send=True, email_values={'email_to': user.email})
                    _logger.info("Email sent to %s (%s)" % (user.name, user.email))
                else:
                    _logger.warning("User %s does not have an email address." % user.name)
        else:
            if not template:
                _logger.warning("Email template 'email_template_general_manager_approver' not found.")
            if not users:
                _logger.warning("No users found in the 'General Managers' group.")

    
   

    