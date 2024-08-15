from odoo import api, fields, models
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = "stock.picking"



    account_manager_id = fields.Char(readonly=True, string="Account Manager", compute="_compute_account_manager_id")
    source_id = fields.Char(readonly=True, string="Source", compute="_source_id")       

    @api.depends('origin')
    def _compute_account_manager_id(self):
        for record in self:
            if record.origin:
                sale_order = self.env['sale.order'].search([('name', '=', record.origin)], limit=1)
                if sale_order:
                    record.account_manager_id = sale_order.account_manager_id.name
                else:
                    record.account_manager_id = None
            else:
                record.account_manager_id = None

    @api.depends('origin')
    def _source_id(self):
        for record in self:
            if record.origin:
                sale_order = self.env['sale.order'].search([('name', '=', record.origin)], limit=1)
                if sale_order:
                    record.source_id = sale_order.opportunity_source_id.name
                else:
                    record.source_id = None
            else:
                record.source_id = None
