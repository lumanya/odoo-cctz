from datetime import datetime, timedelta
from odoo import fields, api, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
from werkzeug.urls import url_encode
import logging

_logger = logging.getLogger(__name__)


class Warranty(models.Model):
    _name = 'warranty.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Warrant Request'
    _order = 'name desc, id desc'


    name = fields.Char(
        string="IR Number",
        required=True, copy=False, readonly=True,    
        default=lambda self: _('New'))
    customer_id = fields.Many2one('res.partner', tracking=True, string="Customer", required=True)
    fault_reported = fields.Char(string='Fault Reported', tracking=True)
    date_received = fields.Date(string='Date Received', tracking=True)
    event_end_date = fields.Date(string='Event End Date', tracking=True)
    job_status = fields.Selection([
        ('open', 'Open'),
        ('unused', 'Unused'),
        ('closed', 'Closed'),
        ('landed paid', 'Landed paid'),
        ('credit note', 'Credit note paid'),
        ('labor paid', 'Labor paid'),
    ], string='Job Status', tracking=True)
    job_category_name = fields.Selection([
        ('Site support', 'Site support'),
        ('Maintance', 'Maintance'),
        ('Normal', 'Normal')
    ])
    technician_assigned = fields.Many2one('hpe.support', string='Technician Assigned')
    type_of_job = fields.Selection([
        ('in house work', 'In house work'),
        ('Job site', 'Job site')
    ], string='Type of Job', tracking=True)
    order_name = fields.Char(string='Order Name')
    order_type = fields.Selection([
        ('warranty order', 'Warranty Order'),
        ('dre order', 'DRE Order')
    ], string='Order Type', tracking=True)
    
    order_status = fields.Selection([
        ('open', 'Open'),
        ('pending part credit', 'Pending Part Credit'),
        ('pending labor', 'Pending Labor'),
        ('pending labor and landed', 'Pending labor and landed'),
        ('pending landed cost', 'Pending Landed Cost'),        
        ('warranty completed', 'Completed')
    ], string='Order Status', tracking=True, default='open', copy=False, required=True, ondelete='restrict')
    order_quantity = fields.Integer(string='Order Quantity', tracking=True)
    product_number = fields.Char(string='Product Number')
    order_date = fields.Datetime(string='Order Date')
    hpe_sales_reference_number = fields.Char(string='HPE Sales Reference Number', tracking=True)
    hpe_reference_number = fields.Char(string='HPE Reference Number')
    hpe_invoice_number = fields.Char(string='HPE Invoice Number')
    hpe_invoice_date = fields.Datetime(string='HPE Invoice Date')
    hpe_invoice_price = fields.Float('HPE Invoice Price', tracking=True)
    equipment_type = fields.Char(string='Equipment Type', tracking=True)
    equipment_serial_number = fields.Char(string='Equipment Serial Number')
    warranty_status = fields.Selection([
        ('HPE 3PAR Storage', 'HPE Storage'),
        ('HPE Server warrant', 'HPE Server'),
        ('HPE Aruba switch', 'HPE Networking'),
    ], string='Warranty Status', tracking=True)
    part_number = fields.Char(string='Order Part Number')
    part_description = fields.Char(string='Part Description')
    part_price = fields.Float('Part Price', tracking=True)
    part_status = fields.Selection([
        ('in stock', 'In Stock'),
        ('ordered', 'Ordered'),
        ('tagged', 'Tagged'),
        ('used', 'Used')
    ], string='Part Status', tracking=True)
    part_arrive_date = fields.Datetime(string='Part Arrive Date', tracking=True)
    part_return_date = fields.Datetime(string='Part Return Date', tracking=True)
    part_return_awb = fields.Char(string='Part Return AWB')
    part_credit_reference = fields.Char(string='Part Credit Reference Number')
    part_credit_received_date = fields.Datetime(string='Part Credit Received Date')
    part_credit_amount = fields.Float('Part Credit Amount', tracking=True)
    part_warranty_status = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ])
    labor_warranty = fields.Char(string='Labor Warranty')
    labor_payment = fields.Float(string='Labor Payment', tracking=True)
    product_number = fields.Char(string='Product Number', tracking=True)
    worksheet_reference_number = fields.Char(string='Worksheet Reference Number', tracking=True)
    awb_number = fields.Char(string='AWB Number')
    clearing_agent = fields.Selection([
        ('dhl', 'DHL'),
        ('ups', 'UPS'),
        ('bollore logistics', 'BOLLORE LOGISTICS')
    ], string='clearing_agent')
    clearing_agent_invoice_number = fields.Char(string='Clearing Agent Invoice Numbe', tracking=True)
    clearing_agent_fees = fields.Char(string='Clearing Agent Fees')
    tag_no_rma = fields.Char(string='Tag No/RMA', tracking=True)
    cc_landed_cost = fields.Float(string='CC Landed Cost (USD)', compute="_compute_cc_landed_cost", tracking=True, store=True)
    hpe_landed_cost = fields.Float(string='HPE Landed Cost (USD)', tracking=True)
    landed_cost_reference = fields.Char(string='Landed Cost Reference', tracking=True)
    landed_cost_date = fields.Datetime(string='Landed Cost Date')
    proposed_labour = fields.Float(string='Proposed Labour')
    ir_number = fields.Char(string='IR Number')
    user_id = fields.Many2one('res.users', string='Warranty', compute='_compute_user', store=True)
    color = fields.Integer('Color Index', default=0)
    claim = fields.Selection([
        ('submited', 'Submited'),
        ('not submited', 'Not Submited')
    ])
    warranty_end_date = fields.Datetime(string='Warranty End Date')
    warranty_request_code = fields.Char(string='Warranty Request Code')
    case_number = fields.Char(string='Case Number')
    case_status = fields.Char(string='Case Status')
    location = fields.Char(string="Location (of work to be done)")
    warranty_end_date = fields.Date(string="Warranty End Date")
    event_number = fields.Char(string='Event number')
    approval_time = fields.Datetime(string="Approval Time", readonly=True)
    second_approval_time = fields.Datetime(string="Second Approval Time", readonly=True)

    exceptional_landed_cost = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Expectional landed cost',default='No') 

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('second_approval', 'Second Approval'),
        ('approved', 'Approved'),
        ('rejected','Rejected')
        ], string='Approval Status', default='draft', track_visibility='onchange', tracking=True)

    regulatory_pt = fields.Float(string="Regulatory-PT (TBS)", tracking=True)
    formal_clearance = fields.Float(string="Formal Clearance (Processing Fee)", tracking=True)
    import_duty = fields.Float(string="Import Duty", tracking=True)
    railway_development_levy = fields.Float(string="Railway Development Levy", tracking=True)
    customs_processing_fee = fields.Float(string="Customs Processing Fee (CPF)", tracking=True)
    eco_levy_fee = fields.Float(string="ECO Levy Fee", tracking=True)
    gcla_fee = fields.Float(string="GCLA Fee", tracking=True)
    storage_fee = fields.Float(string="Storage Fee", tracking=True)
    currency_rate = fields.Float(string="Currency Rate", tracking=True, required=True)

    def action_submit(self):
        self.state = 'to_approve'
        self.approval_time = datetime.now()
        self.send_email_to_managed_service()       


    def action_approve(self):
        self.state = 'second_approval'
        self.second_approval_time = datetime.now()      
        self.send_email_to_head_of_enterprise()
        

    def action_reject(self):
        self.state = 'rejected'
        self.action_send_email()

   

    def action_reject1(self):
        self.state = 'rejected'
        self.action_send_email()


    def action_approve1(self):
        self.state = 'approved'
        self.action_send_email()

   

    menu_id = fields.Integer(string='Menu ID')
    action_id = fields.Integer(string='Action ID')


    # sending email
    def action_send_email(self):
        template = self.env.ref('cctz_warranty.email_warranty_approval_status')
        for rec in self:
            template.send_mail(rec.id, force_send=True)
    

    def _get_managed_service_emails(self):
        manager = self.env['hr.employee'].search([('job_title', '=', 'Services Business Unit Manager')], limit=1) 
        return manager
    
    def send_email_to_managed_service(self):
        manager = self.env['hr.employee'].search([('job_title', '=', 'Services Business Unit Manager')], limit=1)           
        template = self.env.ref('cctz_warranty.email_template_managed_service_approver')    
        
        if template and manager:
            if manager.work_email:
                template.send_mail(self.id, force_send=True, email_values={'email_to': manager.work_email})
                _logger.info("Email sent to %s (%s)" % (manager.name, manager.work_email))
            else:
                _logger.warning("User %s does not have an email address." % manager.name)
        else:
            if not template:
                _logger.warning("Email template 'email_template_managed_service_approver' not found.")
            if not manager:
                _logger.warning("No users found in the 'manager'")  


    def _get_head_of_enterprise_emails(self):
        manager = self.env['hr.employee'].search([('job_title', '=', 'Head of Enterprise')], limit=1) 
        return manager
    
    def send_email_to_head_of_enterprise(self):
        manager = self.env['hr.employee'].search([('job_title', '=', 'Head of Enterprise')], limit=1)           
        template = self.env.ref('cctz_warranty.email_template_head_of_enterprise_approver')    
        
        if template and manager:
            if manager.work_email:
                template.send_mail(self.id, force_send=True, email_values={'email_to': manager.work_email})
                _logger.info("Email sent to %s (%s)" % (manager.name, manager.work_email))
            else:
                _logger.warning("User %s does not have an email address." % manager.name)
        else:
            if not template:
                _logger.warning("Email template 'email_template_head_of_enterprise_approver' not found.")
            if not manager:
                _logger.warning("No users found in the 'manager'")
    
    @api.model
    def generate_link(self):         
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if base_url:
            return f"{base_url}/web#id={self.id}&view_type=form&model={self._name}"
        else:
            return "#"           
    
    #send approval reminders
    def check_approval_reminders(self):
        reminder_time = datetime.now() - timedelta(hours=2)

        to_approve_records = self.search([('state', '=', 'to_approve'), ('approval_time', '<', reminder_time)])
        for record in to_approve_records:
            record.send_reminder_to_manager()

        second_approval_records = self.search([('state', '=', 'second_approval'), ('second_approval_time', '<', reminder_time)])
        for record in second_approval_records:
            record.send_reminder_to_head_enterprise()
    
    def send_reminder_to_manager(self):
        manager = self.env['hr.employee'].search([('job_title', '=', 'Services Business Unit Manager')], limit=1) 
        template = self.env.ref('cctz_warranty.email_template_managed_service_reminder')
        
        if template and manager:
            for user in manager:
                if user.work_email:
                    template.with_context(user=user).send_mail(self.id, force_send=True, email_values={'email_to': user.work_email})
                    _logger.info("Email sent to %s (%s)" % (user.name, user.work_email))
                else:
                    _logger.warning("User %s does not have an email address." % user.name)
        else:
            if not template:
                _logger.warning("Email template 'email_template_loan_officer_approver' not found.")
            if not manager:
                _logger.warning("No users found in the 'Loan Officers' group.")
                
    
    def send_reminder_to_head_enterprise(self):
        manager = self.env['hr.employee'].search([('job_title', '=', 'Head of Enterprise')], limit=1)  
        template = self.env.ref('cctz_warranty.email_template_head_of_enterprise_reminder')
        
        if template and manager:
            for user in manager:
                if user.work_email:
                    template.with_context(user=user).send_mail(self.id, force_send=True, email_values={'email_to': user.work_email})
                    _logger.info("Email sent to %s (%s)" % (user.name, user.work_email))
                else:
                    _logger.warning("User %s does not have an email address." % user.name)
        else:
            if not template:
                _logger.warning("Email template 'email_template_loan_officer_approver' not found.")
            if not manager:
                _logger.warning("No users found in the 'Loan Officers' group.")

    @api.depends('create_uid')
    def _compute_user(self):
        for record in self:
            record.user_id = record.create_uid

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):            
            vals['name'] = self.env['ir.sequence'].next_by_code('warranty.request') or _("New")
        res = super(Warranty, self).create(vals)
        return res
    
    @api.depends('regulatory_pt', 'formal_clearance', 'import_duty', 'railway_development_levy', 
                'customs_processing_fee', 'eco_levy_fee', 'gcla_fee', 'storage_fee', 'currency_rate')
    def _compute_cc_landed_cost(self):
        for record in self:
            total_cost = (
                record.regulatory_pt +
                record.formal_clearance +
                record.import_duty +
                record.railway_development_levy +
                record.customs_processing_fee +
                record.eco_levy_fee +
                record.gcla_fee +
                record.storage_fee
            )
            if record.currency_rate:
                record.cc_landed_cost = total_cost / record.currency_rate
            else:
                record.cc_landed_cost = 0