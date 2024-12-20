from datetime import datetime, timedelta
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
    _order = 'loan_form_number desc, id desc'

    b_state = fields.Selection([
        ('on', 'on'),
        ('off', 'off'),
        ], default='off')
        
    # installment_ids = fields.One2many('loan.installment', 'loan_id', string='Installments')

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
    
    approval_time = fields.Datetime(string="Approval Time", readonly=True)
    second_approval_time = fields.Datetime(string="Second Approval Time", readonly=True)
    third_approval_time = fields.Datetime(string="Third Approval Time", readonly=True)
    
    service_charge = fields.Float(string='service charge', compute= '_calculate_service_charge')
    subtotal = fields.Float(string='subtotal', compute='_calculate_subtotal')
    monthly_rate=fields.Float(string='Monthly Rate', compute='_calculate_monthly_rate')
    monthly_interest=fields.Float(string='Interest', compute='_calculate_monthly_interest')
    total_loan=fields.Float(string='Total Loan', compute='_calculate_Total')

    loan_form_number = fields.Char(string='Loan Form Number', copy=False, readonly=True, required=True, default=lambda self: _('New'))

    attachment_ids = fields.One2many('ir.attachment', 'res_id', string="Attachments")
   
    supported_attachment_ids = fields.Many2many(
        'ir.attachment', string="Attach File", compute='_compute_supported_attachment_ids',
        inverse='_inverse_supported_attachment_ids')
    supported_attachment_ids_count = fields.Integer(compute='_compute_supported_attachment_ids')

    repayment_schedule = fields.Float(string="Avarage Monthly Return", compute='_compute_repayment_schedule')

    _rec_name = 'loan_form_number'

    user_id = fields.Many2one('res.users', string='Loan Requester', compute='_compute_user', store=True, readonly=True)

    loan_officer_id = fields.Many2one('res.users', string="Loan officer", compute="_compute_loan_officer", store=True)

    salary_amount = fields.Integer(string='Salary Amount')
    payment_status = fields.Selection([
        ('outstanding', 'outstanding'),
        ('completed', 'completed'),],
        default='outstanding', string='Payment Status'
    )
    completed_date = fields.Date(string='Loan Completed Date')


    @api.depends('user_id')
    def _compute_loan_officer(self):
        self.loan_officer_id = self.env.user.employee_id.loan_officer_id
     

   
    @api.depends('create_uid')
    def _compute_user(self):
        for record in self:          
            record.user_id = record.create_uid
         

    
    @api.model
    def create(self, vals):
        vals['b_state'] = 'on'
        if vals.get('loan_form_number', _('New'))== _('New'):
            vals['loan_form_number'] = self.env['ir.sequence'].next_by_code('loan.number') or _('New')
        res = super(loanform, self).create(vals)
        res._check_loan_amount()       
        return res
    

    @api.constrains('loan_amount')
    def _check_loan_amount(self):
        for record in self:
            if record.loan_amount == 0:
                raise UserError("Loan amount must not be zero")

    @api.constrains('payment_status')
    def _check_loan_amount(self):
        for record in self:
            if record.state == 'approved' and not record.completed_date:
                raise UserError("Please fill Loan completed Date")

 

    @api.constrains('salary_amount', 'state')
    def _check_salary_amount(self):
        for record in self:
            if record.salary_amount == 0 and self.state == 'second_approval':
                raise UserError("salary amount must not be zero")
            
            
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
            self.state = 'to_approve'
            self.send_email_to_accountant()
            self.approval_time = datetime.now()
        else:
            raise UserError("Please contact your Administrator to set your Loan Officer.")

    employee_id = fields.Many2one('hr.employee', string='Employee', compute='_compute_employee', required=True)

    employee_nida_number = fields.Char(
        string='Employee Identification Number',
        related='employee_id.identification_id',
        store=True,)

    parent_identification_number = fields.Char(
        string=' Manager Identification Number',
        related='employee_id.parent_id.identification_id',
        store=True,)

    loan_officer_name = fields.Char(
        string=' Loan Officer',
        related='employee_id.parent_id.loan_officer_id.name',
        store=True,)

    loan_officer_department = fields.Char(
        string=' Loan Officer Department',
        related='employee_id.loan_officer_id.department_id.name',
        store=True,)

    loan_officer_address = fields.Char(
        string=' Loan Officer Address',
        related='employee_id.loan_officer_id.address_id.name',
        store=True,)



    @api.depends('user_id')
    def _compute_employee(self):
        for record in self:
            employee = self.env['hr.employee'].search([('user_id', '=', record.user_id.id)], limit=1)
            record.employee_id = employee.id


    def action_approve(self):
        self.state = 'second_approval'
        self.second_approval_time = datetime.now()      
        self.send_email_to_loan_officer()
        

    def action_reject(self):
        self.state = 'rejected'
        self.action_send_email()


    def action_approve1(self):
        self.state = 'third_approval'
        self.third_approval_time = datetime.now()         
        self.send_email_to_general_manager()

    def action_reject1(self):
        self.state = 'rejected'
        self.action_send_email()


    def action_approve2(self):
        self.state = 'approved'
        self.action_send_email()
        self.action_send_instruction_notification()

    def action_reject2(self):
        self.state = 'rejected'
        self.action_send_email()

    menu_id = fields.Integer(string='Menu ID')
    action_id = fields.Integer(string='Action ID')
   
   
    def send_approval_reminders(self):
        reminder_time = datetime.now() - timedelta(days=1)

        to_approve_records = self.search([('state', '=', 'to_approve'), ('approval_time', '<', reminder_time)])
        for record in to_approve_records:
            record.send_reminder_to_accountant()

        second_approval_records = self.search([('state', '=', 'second_approval'), ('second_approval_time', '<', reminder_time)])
        for record in second_approval_records:
            record.send_reminder_to_loan_officer()
            
        third_approval_records = self.search([('state', '=', 'third_approval'), ('third_approval_time', '<', reminder_time)])
        for record in third_approval_records:
            record.send_reminder_to_managers() 
            
    
    def send_reminder_to_loan_officer(self):
        users = self.create_uid.employee_id.loan_officer_id
        template = self.env.ref('loan_form.email_template_loan_officer_reminder')
        
        if template and users:
            for user in users:
                if user.work_email:
                    template.with_context(user=user).send_mail(self.id, force_send=True, email_values={'email_to': user.work_email})
                    _logger.info("Email sent to %s (%s)" % (user.name, user.work_email))
                else:
                    _logger.warning("User %s does not have an email address." % user.name)
        else:
            if not template:
                _logger.warning("Email template 'email_template_loan_officer_approver' not found.")
            if not users:
                _logger.warning("No users found in the 'Loan Officers' group.")

          
    def send_reminder_to_accountant(self):
        accountant = self.env['hr.employee'].search([('job_title', '=', 'Head of Procurement & Accountant')], limit=1)           
        template = self.env.ref('loan_form.email_template_accountant_reminder')    
        
        if template and accountant:
            if accountant.work_email:
                template.send_mail(self.id, force_send=True, email_values={'email_to': accountant.work_email})
                _logger.info("Email sent to %s (%s)" % (accountant.name, accountant.work_email))
            else:
                _logger.warning("User %s does not have an email address." % accountant.name)
        else:
            if not template:
                _logger.warning("Email template 'email_template_accountant_approver' not found.")
            if not accountant:
                _logger.warning("No users found in the 'Accountant'")

          
    def send_reminder_to_managers(self):
        manager = self.env['hr.employee'].search([('job_title', '=', 'General Manager')], limit=1)           
        template = self.env.ref('loan_form.email_template_manager_reminder')    
        
        if template and manager:
            if manager.work_email:
                template.send_mail(self.id, force_send=True, email_values={'email_to': manager.work_email})
                _logger.info("Email sent to %s (%s)" % (manager.name, manager.work_email))
            else:
                _logger.warning("User %s does not have an email address." % manager.name)
        else:
            if not template:
                _logger.warning("Email template 'email_template_general_manager_approver' not found.")
            if not manager:
                _logger.warning("No users found in the 'manager'")  


    @api.model
    def generate_link(self):         
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if base_url:
            return f"{base_url}/web#id={self.id}&view_type=form&model={self._name}"
        else:
            return "#"
        
        
    def _get_my_records(self):
        return self.search([('create_uid', '=', self.env.uid)])
   
    # sending email
    def action_send_email(self):
        template = self.env.ref('loan_form.email_loan_approval_status')
        for rec in self:
            template.send_mail(rec.id, force_send=True)
            
    def action_send_instruction_notification(self):
        template = self.env.ref('loan_form.email_loan_approval_status_notify')
        for rec in self:
            template.send_mail(rec.id, force_send=True)

    
    def _get_loan_officer_emails(self):
        users = self.create_uid.employee_id.loan_officer_id
        return [user for user in users if user.email]
    
    def send_email_to_loan_officer(self):
        users = self.create_uid.employee_id.loan_officer_id
        template = self.env.ref('loan_form.email_template_loan_officer_approver')
        
        if template and users:
            for user in users:
                if user.work_email:
                    template.with_context(user=user).send_mail(self.id, force_send=True, email_values={'email_to': user.work_email})
                    _logger.info("Email sent to %s (%s)" % (user.name, user.work_email))
                else:
                    _logger.warning("User %s does not have an email address." % user.name)
        else:
            if not template:
                _logger.warning("Email template 'email_template_loan_officer_approver' not found.")
            if not users:
                _logger.warning("No users found in the 'Loan Officers' group.")

    
  

    def _get_accountant_emails(self):
        accountant = self.env['hr.employee'].search([('job_title', '=', 'Head of Procurement & Accountant')], limit=1)
        return accountant

    
    def send_email_to_accountant(self):

        accountant = self.env['hr.employee'].search([('job_title', '=', 'Head of Procurement & Accountant')], limit=1)           
        template = self.env.ref('loan_form.email_template_accountant_approver')    
        
        if template and accountant:
            if accountant.work_email:
                template.send_mail(self.id, force_send=True, email_values={'email_to': accountant.work_email})
                _logger.info("Email sent to %s (%s)" % (accountant.name, accountant.work_email))
            else:
                _logger.warning("User %s does not have an email address." % accountant.name)
        else:
            if not template:
                _logger.warning("Email template 'email_template_accountant_approver' not found.")
            if not accountant:
                _logger.warning("No users found in the 'Accountant'")


    def _get_general_manager_emails(self):
        manager = self.env['hr.employee'].search([('job_title', '=', 'General Manager')], limit=1) 
        return manager
    
    def send_email_to_general_manager(self):
        manager = self.env['hr.employee'].search([('job_title', '=', 'General Manager')], limit=1)           
        template = self.env.ref('loan_form.email_template_general_manager_approver')    
        
        if template and manager:
            if manager.work_email:
                template.send_mail(self.id, force_send=True, email_values={'email_to': manager.work_email})
                _logger.info("Email sent to %s (%s)" % (manager.name, manager.work_email))
            else:
                _logger.warning("User %s does not have an email address." % manager.name)
        else:
            if not template:
                _logger.warning("Email template 'email_template_general_manager_approver' not found.")
            if not manager:
                _logger.warning("No users found in the 'manager'")  

    @api.depends('payment_status')
    def action_completed(self):
        self.ensure_one()
        if self.payment_status == 'outstanding':
            self.payment_status = 'completed'

   