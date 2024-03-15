from odoo import models, fields


class InheritHrEmployee(models.Model):
    _inherit = "hr.employee"

    # Add your new fields here
    loan_officer_id = fields.Many2one('res.users', string='Loan Officer')

    

    
