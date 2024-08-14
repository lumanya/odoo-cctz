from odoo import models, fields, api,_

class asset_registration(models.Model):
    _name = 'asset.registration'
    _inherit = 'mail.thread'
    _description = 'Asset'
    
    asset_number = fields.Char(string='Asset Number', copy=False, readonly=True, required=True, default=lambda self: _('New'))

    asset_name = fields.Char(string= 'Asset Name',required=True)
    date = fields.Date(string = 'Receiving Date', required=True)
    supplier_id = fields.Many2one('res.partner', string= 'Supplier Name', required=True)
    order_number = fields.Char(string='Order number', required=True)
    device_part_number = fields.Char(string='Device Part Number', required=True)
    quantity = fields.Integer(string= 'Quantity', required=True)
    description = fields.Text(string= 'Description')

    @api.model
    def create(self, vals):
        if vals.get('asset_number', _('New'))== _('New'):
            vals['asset_number'] = self.env['ir.sequence'].next_by_code('asset.number') or _('New')
        res = super(asset_registration, self).create(vals)    
        return res

