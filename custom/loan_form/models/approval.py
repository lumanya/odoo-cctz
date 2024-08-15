from odoo import models, fields


class Approvals(models.Model):
    _name = "loan.approval"
    _description = "Approvals of Loan Request"

    head_of_accountant = fields.Many2one('res.users', string='Head of Accountant', store=True)

    general_manager = fields.Many2one('res.users', string='General Manager', store=True)