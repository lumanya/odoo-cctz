from odoo import models, fields, api,_

class asset_registration(models.Model):
    _name = 'asset.registration'
    _inherit = 'mail.thread'
    _description = 'Asset'
    
    asset_number = fields.Char(string='Asset Number', copy=False, readonly=True, required=True, store=True, default=lambda self: _('New'))

    asset_name = fields.Char(string= 'Asset Name',required=True)
    date = fields.Date(string = 'Receiving Date', required=True)

    # for_company_use = fields.Boolean(string='For company Use', default= False)

    supplier_id = fields.Many2one(
        'res.partner', 
        string= 'Supplier Name', 
        required=False
        )
    
    
    device_part_number = fields.Char(string='Device Part Number', required=True)

    quantity = fields.Integer(string= 'Quantity', required=True)

    description = fields.Text(string= 'Description')

    # @api.onchange('purchase_id')
    # def _onchange_purchase_id(self):
    #     if self.purchase_id:
    #         self.supplier_id = self.purchase_id.partner_id.id

    # @api.onchange('for_company_use')
    # def _onchange_for_company_use(self):
    #     if self.for_company_use:
    #         self.purchase_id = False  # Clear the order field
    #         self.supplier_id = False  # Clear the supplier field
    #     else:
          
    #         pass

    @api.model
    def create(self, vals):
        if vals.get('asset_number', _('New'))== _('New'):
            vals['asset_number'] = self.env['ir.sequence'].next_by_code('asset.number') or _('New')
        res = super(asset_registration, self).create(vals)    
        return res
    

