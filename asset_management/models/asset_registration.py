from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class asset_registration(models.Model):
    _name = 'asset.registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Asset'
    
    asset_number = fields.Char(string='Asset Number', copy=False, readonly=True, required=True, store=True, default=lambda self: _('New'))

    asset_name_id = fields.Many2one(
        'product.product', 
        string= 'Asset Name',
        required=True,
        )
    
    date = fields.Date(string = 'Receiving Date', required=True, default=fields.Date.context_today)

    device_purpose = fields.Selection([
        ('service_delivery','Service-Delivery Asset'), 
        ('employee_assigned', 'Employee Asset'), 
        ('operational_support', 'Operational Support Asset')
        ], string='Asset Type', required=True)

    supplier_id = fields.Many2one(
        'res.partner', 
        string= 'Supplier Name', 
        required=False
        )
    
    current_location = fields.Many2one('hr.department', string="Current Location")
    
    invoice_number = fields.Char(string='Invoice number') 
    device_part_number = fields.Char(string='Serial Number/Part Number', required=False)

    quantity = fields.Integer(string= 'Quantity', required=True, default = 1)

    description = fields.Text(string= 'Description', store=True) 
    
    total_assets = fields.Integer(string='Total Assets', compute='_compute_total_assets')
    
    total_quantity = fields.Integer(string='Total Quantity', compute='_compute_total_quantity')

    
    def name_get(self):
        result = []
        for record in self:
            name = f'{record.asset_number}'
            result.append((record.id, name))
        return result

    @api.model
    def create(self, vals):
        if vals.get('device_purpose') == 'operational_support' and not vals.get('device_part_number'):
            vals['device_part_number'] = self.env['ir.sequence'].next_by_code('asset.serial.number') or _('Auto-Generated')
            
        if vals.get('asset_number', _('New'))== _('New'):
            vals['asset_number'] = self.env['ir.sequence'].next_by_code('asset.number') or _('New')
        
        res = super(asset_registration, self).create(vals)

        move_vals = {
            'asset_id': res.id,
            'move_date':fields.Date.today(),
            'device_purpose': res.device_purpose,
            'current_location_move':res.current_location,
            'move_number': self.env['ir.sequence'].next_by_code('asset.move.number') or _('New'),
        } 

        self.env['asset.move'].create(move_vals)
           
        return res
    
    @api.constrains('quantity')
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError("Quantity must be greater than zero.")
            
    @api.depends('quantity')
    def _compute_total_assets(self):
        for record in self:
            record.total_assets = self.search_count([])

    @api.depends('quantity')
    def _compute_total_quantity(self):
        for record in self:
            total_qty = sum(asset.quantity for asset in self.search([]))
            record.total_quantity = total_qty

