from odoo import models, fields


class InheritHrEmployee(models.Model):
    _inherit = "hr.employee"

    loan_officer_id = fields.Many2one('res.users', string='Loan Officer', groups="hr.group_hr_user")

    

    
