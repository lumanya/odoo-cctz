from odoo import models, fields, api,_

class asset_registration(models.Model):
    _name = 'asset.registration'
    _inherit = 'mail.thread'
    _description = 'Asset'
    
    asset_number = fields.Char(string='Asset Number', copy=False, readonly=True, required=True, store=True, default=lambda self: _('New'))

    asset_name_id = fields.Many2one(
        'product.product', 
        string= 'Asset Name',
        required=True,
        )
    
    date = fields.Date(string = 'Receiving Date', required=True, default=fields.Date.context_today)

    device_purpose = fields.Selection([
        ('customer', 'Customer'), 
        ('employee', 'Employee'), 
        ('technician', 'Technician')
        ], string='Device Purpose', required=True)

    supplier_id = fields.Many2one(
        'res.partner', 
        string= 'Supplier Name', 
        required=False
        )
    
    invoice_number = fields.Char(string='Invoice number', required=True) 
    device_part_number = fields.Char(string='Device Part Number', required=True)

    quantity = fields.Integer(string= 'Quantity', required=True)

    description = fields.Char(related='asset_name_id.name', string= 'Description') 

    

    def name_get(self):
        result = []
        for record in self:
            name = f'{record.asset_number}'
            result.append((record.id, name))
        return result

    @api.model
    def create(self, vals):
        if vals.get('asset_number', _('New'))== _('New'):
            vals['asset_number'] = self.env['ir.sequence'].next_by_code('asset.number') or _('New')
        res = super(asset_registration, self).create(vals)

        move_vals = {
            'asset_id': res.id,
            'move_date':fields.Date.today(),
            'device_purpose': res.device_purpose
        } 

        self.env['asset.move'].create(move_vals)
           
        return res
    

