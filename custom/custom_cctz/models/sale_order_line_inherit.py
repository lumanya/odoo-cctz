from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"


    price_unit = fields.Float( 
        string="Unit Price",      
        compute='_compute_price_unit',
        digits='Product Price',
        store=True, readonly=True, precompute=True, tracking=True)
    
    margin = fields.Float(
        "Margin", compute='_compute_margin',
        digits='Product Price', store=True, groups="base.group_user", precompute=True)
    margin_percent = fields.Float(
        "Margin (%)", store=True, groups="base.group_user")
    purchase_price = fields.Float(
        string="Cost", compute="_compute_purchase_price",
        digits='Product Price', store=True, readonly=False, precompute=True,
        groups="base.group_user")
    
    part_number_id = fields.Char(
        string='Part Number', 
        compute="_compute_part_number",
        readonly=False, store=True, required=True)    
   

    manufacturer_id = fields.Many2one(comodel_name='manufacturer',
    readonly=False, precompute=True, store=True,
    compute='_compute_manufacturer_id',
    string='Manufacturer', required=True)

    business_unit_id = fields.Many2one(comodel_name='crm.team', readonly=False,
     precompute=True, store=True, string='Business Unit', compute="_compute_business_unit_id", required=True)

    supplier_id = fields.Many2one(comodel_name='res.partner', readonly=False, precompute=True,
     store=True, string='Supplier', compute="_compute_supplier_id", required=True)

  
    renewal_duration = fields.Selection([
    ('1', '1 Year'),
    ('2', '2 Years'),
    ('3', '3 Years'),
    ('4', '4 Years'),
    ('5', '5 Years')
    ], string='Renewal Duration', required=True)

    is_renewal = fields.Boolean(default=False, required=True)
    renewal_visible = fields.Boolean(compute='_compute_renewal_visibility')

    @api.depends('renewal_duration', 'is_renewal')
    def _compute_renewal_visibility(self):
        for product in self:
            product.renewal_visible = product.is_renewal
    


    @api.depends('product_id')
    def _compute_part_number(self):
        for line in self:
            line.part_number_id = line.product_id.part_number

    @api.depends('product_id')
    def _compute_manufacturer_id(self):
        for line in self:
            line.manufacturer_id = line.product_id.manufacturer_id

    @api.depends('product_id')
    def _compute_business_unit_id(self):
        for line in self:
            line.business_unit_id = line.product_id.business_unit_id
    
    @api.depends('product_id')
    def _compute_supplier_id(self):
        for line in self:
            line.supplier_id = line.product_id.supplier_id


    @api.onchange('business_unit_id')
    def _onchange_business_unit_id(self):
        self.product_id.business_unit_id = self.business_unit_id

    @api.onchange('manufacturer_id')
    def _onchange_manufacturer_id(self):
        self.product_id.manufacturer_id = self.manufacturer_id

    @api.onchange('part_number_id')
    def _onchange_part_number_id(self):
        self.product_id.part_number = self.part_number_id

    @api.onchange('renewal_duration')
    def _onchange_renewal_duration(self):
        self.product_id.renewal_duration = self.renewal_duration

   


    @api.depends('price_subtotal', 'product_uom_qty', 'purchase_price')
    def _compute_margin(self):
        for line in self:
            line.margin = (line.margin_percent * line.purchase_price) * line.product_uom_qty
            #line.margin_percent = line.margin_percent
        

    @api.depends('product_id', 'product_uom', 'product_uom_qty', 'margin_percent', 'purchase_price')
    def _compute_price_unit(self):
        for line in self:
          
            # check if there is already invoiced amount. if so, the price shouldn't change as it might have been
            # manually edited
            if line.qty_invoiced > 0:
                continue
            if not line.product_uom or not line.product_id or not line.order_id.pricelist_id:
                line.price_unit = 0.0
            else:                
                print(" ========= PERCENT ======== ")
                print(line.margin_percent)
                margin = line.purchase_price * line.margin_percent
                print("Margin:", margin)
                price =  line.purchase_price + margin
                print("Price:", price)
                line.price_unit = line.product_id._get_tax_included_unit_price(
                    line.company_id,
                    line.order_id.currency_id,
                    line.order_id.date_order,
                    'sale',
                    fiscal_position=line.order_id.fiscal_position_id,
                    product_price_unit=price,
                    product_currency=line.currency_id
                )

 
