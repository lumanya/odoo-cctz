from odoo import fields, api, models, _   


class InheritProductTemplate(models.Model):
    _inherit = 'product.template'

    part_number = fields.Char(string="Part Number")
    business_unit_id = fields.Many2one('crm.team', string="Business Unit", required=True)
    manufacturer_id = fields.Many2one('manufacturer', string="Manufacturer", required=True)
    supplier_id = fields.Many2one('res.partner', string="Supplier")
    renewal_duration = fields.Selection([
    ('1', '1 Year'),
    ('2', '2 Years'),
    ('3', '3 Years'),
    ('4', '4 Years'),
    ('5', '5 Years')
    ], string='Renewal Duration', required=True)

    is_renewal = fields.Boolean(default=False)
    renewal_visible = fields.Boolean(compute='_compute_renewal_visibility')

    @api.depends('renewal_duration', 'is_renewal')
    def _compute_renewal_visibility(self):
        for product in self:
            product.renewal_visible = product.is_renewal