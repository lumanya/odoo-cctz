from odoo import models, fields, api, _


class LoanInstallment(models.Model):
    _name = "loan.installment"
    _description = 'Loan Installment'
    _order = 'name desc, id desc'

    name = fields.Char(
        string="Installment Number",
        required=True, copy=False, readonly=True,    
        default=lambda self: _('New'))

    loan_id = fields.Many2one('loan.form', string='Loan Form', required=True)
    amount = fields.Float(string='Installment Amount', required=True)    
    payment_date = fields.Date(string='Payment Date')
    user_id = fields.Many2one('res.users', string='Accountant', compute='_compute_user', store=True, readonly=True)

    status = fields.Selection([
        ('pending', 'Pending'),
        ('paid', 'Paid'),       
    ], string='Status', store=True)

    loan_requester_id = fields.Many2one('res.users', string='Loan Requester', compute='_compute_loan_requester', store=True, readonly=True)


    @api.depends('create_uid')
    def _compute_user(self):
        for record in self:          
            record.user_id = record.create_uid

    @api.depends('loan_id')
    def _compute_loan_requester(self):
        for record in self:
            record.loan_requester_id = record.loan_id.user_id

    
    @api.model
    def create(self, vals):
        if vals.get('name', _("New")) == _("New"):            
            vals['name'] = self.env['ir.sequence'].next_by_code('loan.installment') or _("New")
        res = super(LoanInstallment, self).create(vals)
        return res

    

    
