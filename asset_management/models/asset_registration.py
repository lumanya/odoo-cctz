from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class asset_registration(models.Model):
    _name = 'asset.registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Asset'
    _order = 'create_date desc'
    
    asset_number = fields.Char(string='Asset Number', copy=False, readonly=True, required=True, store=True, default=lambda self: _('New'))

    asset_name_id = fields.Many2one(
        'product.product', 
        string= 'Asset Name',
        required=True,
        )
    
    price_unit = fields.Float(string='Unit Price', compute='_compute_price_unit', store=True)    
    depreciation_method = fields.Selection([
        ('straight_line', 'Straight Line'),
        ('declining_balance', 'Declining Balance'),
    ], string='Depreciation Method', default='straight_line')    
    depreciation_rate = fields.Float(string='Depreciation Rate (%)', required=True)    
    depreciation_period = fields.Selection([
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
    ], string='Depreciation Period', default='yearly')    
    cumulative_depreciation = fields.Float(string='Cumulative Depreciation', compute='_compute_depreciation')    
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)    
    net_book_value = fields.Float(string='Net Book Value', compute='_compute_net_value', store=True)    
    state = fields.Selection([
    ('fully_depreciated', 'Fully Depreciated'),
    ('non_depreciated', 'Non-Depreciated'),
    ], string='Depreciation State', compute='_compute_state', store=True)    
    fully_depreciated_count = fields.Integer(string='Fully Depreciated Assets', compute='_compute_fully_depreciated_count', store=True)    
    non_depreciated_count = fields.Integer(string='Non-Depreciated Assets', compute='_compute_non_depreciated_count', store=True)
    depreciation_start_date = fields.Date(string="Depreciation Start Date", required=True, default=fields.Date.context_today)
    depreciation_end_date = fields.Date(string="Depreciation End Date", compute='_compute_depreciation_end_date', store=True)
    depreciation_duration = fields.Integer(string='Depreciation Duration (Months)', compute='_compute_depreciation_duration', store=True)    
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
    current_location = fields.Many2one('hr.department', string="Current Location", store=True)    
    asset_count = fields.Integer(string='Number of Assets', compute='_compute_asset_count', store=True)    
    invoice_number = fields.Char(string='Invoice number') 
    device_part_number = fields.Char(string='Serial Number/Part Number', required=False)
    quantity = fields.Integer(string= 'Quantity', required=True, default = 1)
    description = fields.Text(string= 'Description', store=True)     
    total_assets = fields.Integer(string='Total Assets', compute='_compute_total_assets', store=True)    
    total_quantity = fields.Integer(string='Total Quantity', compute='_compute_total_quantity')    
    warranty_start_date = fields.Date(string='Warranty Start Date')    
    warranty_end_date = fields.Date(string='Warranty End Date')
    asset_category = fields.Selection([
        ('furnitures', 'Furnitures'),
        ('computers', 'Computers'),
        ('tools', 'Tools')
    ], string='Asset Category', required=True)

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
            'current_location_move':res.current_location.id,
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
        total = self.env['asset.registration'].search_count([])
        for record in self:
            record.total_assets = total
            
    @api.depends('current_location')
    def _compute_asset_count(self):
        for record in self:
            if record.current_location and record.device_purpose == 'operational_support':
                record.asset_count = self.env['asset.registration'].search_count([
                    ('current_location', '=', record.current_location.id)
                ])
            else:
                record.asset_count = 0
                        
    @api.depends('quantity')
    def _compute_total_quantity(self):
        for record in self:
            total_qty = sum(asset.quantity for asset in self.search([]))
            record.total_quantity = total_qty
            
    @api.depends('asset_name_id')
    def _compute_price_unit(self):
        for record in self:
            if record.asset_name_id:
                record.price_unit = record.asset_name_id.list_price
            else:
                record.price_unit = 0.0
                
    @api.depends('depreciation_start_date', 'price_unit', 'depreciation_rate', 'depreciation_period', 'depreciation_method')
    def _compute_depreciation_end_date(self):
        for record in self:
            if record.depreciation_method == 'straight_line':
                depreciation_per_period = (record.price_unit * (record.depreciation_rate / 100))
                
                if depreciation_per_period > 0:
                    # Calculate how many periods are needed for the asset value to become 0
                    if record.depreciation_period == 'yearly':
                        total_periods = record.price_unit / depreciation_per_period
                        record.depreciation_end_date = fields.Date.add(record.depreciation_start_date, years=int(total_periods))
                    elif record.depreciation_period == 'monthly':
                        total_periods = record.price_unit / (depreciation_per_period / 12)
                        record.depreciation_end_date = fields.Date.add(record.depreciation_start_date, months=int(total_periods))
                else:
                    record.depreciation_end_date = record.depreciation_start_date  # Or set it to a default/fallback date
            elif record.depreciation_method == 'declining_balance':
                # For declining balance, more complex, with faster depreciation at the beginning
                total_periods = 0
                current_value = record.price_unit
                depreciation_rate = record.depreciation_rate / 100
                
                if depreciation_rate > 0:
                    if record.depreciation_period == 'yearly':
                        while current_value > 0.01:  # Threshold for when to stop depreciating
                            current_value -= (current_value * depreciation_rate)
                            total_periods += 1
                        record.depreciation_end_date = fields.Date.add(record.depreciation_start_date, years=total_periods)
                    elif record.depreciation_period == 'monthly':
                        while current_value > 0.01:
                            current_value -= (current_value * depreciation_rate / 12)
                            total_periods += 1
                        record.depreciation_end_date = fields.Date.add(record.depreciation_start_date, months=total_periods)
                else:
                    record.depreciation_end_date = record.depreciation_start_date  # Or set it to a default/fallback date


    @api.depends('depreciation_start_date', 'depreciation_end_date')
    def _compute_depreciation_duration(self):
            for record in self:
                start_date = fields.Date.from_string(record.depreciation_start_date)
                end_date = fields.Date.from_string(record.depreciation_end_date)
                record.depreciation_duration = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                    
        
    @api.depends('price_unit', 'depreciation_rate', 'depreciation_period')
    def _compute_depreciation(self):
            for record in self:
                if record.depreciation_method == 'straight_line':
                    depreciation_per_period = (record.price_unit * (record.depreciation_rate / 100))
                    if record.depreciation_period == 'yearly':
                        record.cumulative_depreciation = depreciation_per_period
                    elif record.depreciation_period == 'monthly':
                        record.cumulative_depreciation = depreciation_per_period / 12
                elif record.depreciation_method == 'declining_balance':
                    depreciation_per_period = (record.price_unit * (record.depreciation_rate / 100))
                    if record.depreciation_period == 'yearly':
                        record.cumulative_depreciation = depreciation_per_period
                    elif record.depreciation_period == 'monthly':
                        record.cumulative_depreciation = depreciation_per_period / 12
                    
    @api.depends('price_unit','cumulative_depreciation')
    def _compute_net_value(self):
        for record in self:
            record.net_book_value = record.price_unit - record.cumulative_depreciation

    @api.depends('net_book_value')
    def _compute_fully_depreciated_count(self):
        for record in self:
            record.fully_depreciated_count = self.search_count([
                ('net_book_value', '=', 0.0)
            ])
            
    @api.depends('net_book_value')
    def _compute_non_depreciated_count(self):
        for record in self:
            record.non_depreciated_count = self.search_count([
                ('net_book_value', '>', 0.0)
            ])
            
    @api.depends('fully_depreciated_count', 'non_depreciated_count')
    def _compute_state(self):
        for record in self:
            if record.fully_depreciated_count:
                record.state = 'fully_depreciated'
            else:
                record.state = 'non_depreciated'