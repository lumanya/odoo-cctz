from odoo import models, fields, api,_
from odoo.exceptions import UserError

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
        ('approved', 'Approved'),
        ('rejected','Rejected')
        ], string='Status', default='draft', track_visibility='onchange', tracking=True)

    active = fields.Boolean(default=True, readonly=True)

    loan_amount = fields.Integer(string='Loan amount')
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
    default='1'
    )
    reason = fields.Text(string='Reason')
    constant = fields.Float(default=0.01)
    constant1 = fields.Float(default=0.005)

    attach_files = fields.Binary(string='Attachment')

    service_charge = fields.Float(string='service charge', compute= '_calculate_service_charge')
    subtotal = fields.Float(string='subtotal', compute='_calculate_subtotal')
    monthly_rate=fields.Float(string='Monthly Rate', compute='_calculate_monthly_rate')
    monthly_interest=fields.Float(string='Monthly Interest', compute='_calculate_monthly_interest')
    total_loan=fields.Float(string='Total Loan', compute='_calculate_Total')

    loan_form_number = fields.Char(string='Loan Form Number', copy=False, readonly=True, required=True, default=lambda self: _('New'))

    attachment_ids = fields.One2many('ir.attachment', 'res_id', string="Attachments")
   
    supported_attachment_ids = fields.Many2many(
        'ir.attachment', string="Attach File", compute='_compute_supported_attachment_ids',
        inverse='_inverse_supported_attachment_ids')
    supported_attachment_ids_count = fields.Integer(compute='_compute_supported_attachment_ids')

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
            self.state = 'to_approve'
        else:
            raise UserError("Please contact your Administrator to set your Loan Officer.")

        
    def action_approve(self):
        self.state = 'approved'

    def action_reject(self):
        self.state = 'rejected'

