from queue import Full
from odoo import models, fields, api,_
class AssetMove(models.Model):
    _name = 'asset.move'
    _inherit = 'mail.thread'
    _description = 'Asset Move'
    _order = 'create_date desc'

    asset_id = fields.Many2one(
        'asset.registration',
        string='Asset',
        required=True,
        readonly=True,
    )

    # device_purpose = fields.Selection([
    #     ('customer', 'Customer'),
    #     ('employee', 'Employee'),
    #     ('technician', 'Technician'),
    # ], string= 'Device Purpose',required=True)

    move_number = fields.Char(string='Move Number', copy=False, readonly=True, required=True, store=True)

    asset_name = fields.Many2one(related='asset_id.asset_name_id', string='Asset Name', readonly=True, required=True)

    date = fields.Date(related='asset_id.date', string='Receiving Date', readonly=True)

    device_purpose = fields.Selection(related='asset_id.device_purpose', string='Asset Type', readonly=True)

    supplier_id = fields.Many2one(related='asset_id.supplier_id', string='Supplier Name', readonly=True)

    # invoice_number = fields.Char(related='asset_id.invoice_number', string='Invoice Number', readonly=True, store=True)

    device_part_number = fields.Char(related='asset_id.device_part_number', string='Serial Number/Part Number', readonly=True, store=True)

    quantity = fields.Integer(related='asset_id.quantity', string='Quantity', readonly=True, store=True)

    description = fields.Text(related='asset_id.description', string='Description', readonly=True, store=True)

    display_description = fields.Char(string='Description', compute='_compute_display_description')
    
    move_date = fields.Date(string='Movement Date', required=True)

    # order_id = fields.Many2one('sale.order', string='Order Number')

    # customer_id = fields.Many2one('res.partner', string='Customer', domain="[('customer_rank', '>', 0)]")

    # sales_id = fields.Many2one('res.users', string='Sales Person')

    technician_id_move = fields.Many2one('res.users', string='Technician')

    employee_id_move = fields.Many2one('hr.employee', string='Employee')
    
    status_tech = fields.Selection([('in_use', 'In Use'), ('available', 'Available')], string='Availability', default ='available', readonly=True)
    
    status = fields.Selection([('assigned', 'Assigned'), ('returned','Returned')], string='Status', default = 'assigned', required=True)
    
    return_date = fields.Date(string='Return Date')

    return_condition = fields.Selection([('good', 'Good'), ('repairable', 'Repairable'), ('damaged', 'Damaged')], string='Device Condition', default='good',readonly=True)

    # invoice_status = fields.Selection([
    #     ('to_be_invoiced', 'To be Invoiced'),
    #     ('invoiced', 'Invoiced'),
    #     ('pending', 'Pending'),
    # ], string='Remarks', default='pending', track_visibility='onchange', tracking= True,required=True)
    
    invoice_number_move = fields.Char(string='Invoice Number')
    
    asset_move_history_ids = fields.One2many('asset.move.history', 'asset_move_id', string='History')
    
    asset_move_employee_ids = fields.One2many('asset.move.employee', 'asset_employee_id', string='Employee History')
    
    current_location_move = fields.Char(related='asset_id.current_location', string='Current Location', readonly=True)
    
    asset_oprational_move_ids = fields.One2many('asset.operational.move', 'asset_operational_id', string='Operational Asset Asset' )

    # invoice_status = fields.Selection(related='order_id.invoice_status', string='Invoice Status')
    # @api.model
    # def create(self,vals):        
    #     if vals.get('invoice_status') in ['to_be_invoiced', 'pending']:
    #         vals['invoice_number_move'] = False
    #     return super(AssetMove, self).create(vals)
    
    # def write(self, vals):
    #     if 'invoice_status' in vals and vals['invoice_status'] in ['to_be_invoiced', 'pending']:
    #         vals['invoice_number_move'] = False
    #     return super(AssetMove, self).write(vals)
    
    def name_get(self):
        result = []
        for record in self:
            name = f'{record.move_number}'
            result.append((record.id, name))
        return result
    
    @api.onchange('status')
    def _onchange_status(self):
        if self.status == 'returned':
            self.return_date = fields.Date.today()

    @api.onchange('device_purpose')
    def _onchange_device_purpose(self):
        # self.customer_id = False
        self.technician_id_move = False
        self.employee_id_move = False
        # if self.device_purpose != 'for_customer':
        #     self.order_id = False
        
    @api.depends('description')
    def _compute_display_description(self):
        for record in self:
            record.display_description = record.description if record.description else 'There is no description'


    # @api.onchange('order_id')
    # def onchange_order_id(self):
    #     if self.order_id:
    #         self.customer_id = self.order_id.partner_id
    #         self.sales_id = self.order_id.user_id


    def action_confirm(self):
        self.write({'state': 'done'})  