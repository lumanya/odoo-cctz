from odoo import api, fields, models
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = "stock.move"

    business_unit_id = fields.Many2one(comodel_name='crm.team', readonly=True,
     precompute=True, store=True, string='Business Unit', compute="_compute_business_unit_id")

    

    @api.depends('product_id')
    def _compute_business_unit_id(self):
        for line in self:
            line.business_unit_id = line.product_id.business_unit_id

    