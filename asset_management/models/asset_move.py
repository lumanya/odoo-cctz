from odoo import models, fields, api,_
class AssetMove(models.Model):
    _name = 'asset.move'
    _inherit = 'mail.thread'
    _description = 'Asset Move'

    asset_id = fields.Many2one(
        'asset.registration',
        string='Asset',
        required=True,
        readonly=True,
    )

    device_purpose = fields.Selection([
        ('customer', 'Customer'),
        ('employee', 'Employee'),
        ('technician', 'Technician'),
    ], string= 'Device Purpose',required=True)


    asset_name = fields.Char(related='asset_id.asset_name', string='Asset Name', readonly=True, store=True)

    date = fields.Date(related='asset_id.date', string='Receiving Date', readonly=True)

    device_purpose = fields.Selection(related='asset_id.device_purpose', string='Device Purpose', readonly=True)

    supplier_id = fields.Many2one(related='asset_id.supplier_id', string='Supplier Name', readonly=True)

    invoice_number = fields.Char(related='asset_id.invoice_number', string='Invoice Number', readonly=True, store=True)

    device_part_number = fields.Char(related='asset_id.device_part_number', string='Device Part Number', readonly=True, store=True)

    quantity = fields.Integer(related='asset_id.quantity', string='Quantity', readonly=True, store=True)

    description = fields.Text(related='asset_id.description', string='Description', readonly=True, store=True)

    move_date = fields.Date(string='Movement Date', required=True)

    order_id = fields.Many2one('sale.order', string='Order Number')

    customer_id = fields.Many2one('res.partner', string='Customer', domain="[('customer_rank', '>', 0)]")

    sales_id = fields.Many2one('res.users', string='Sales Person')

    technician_id = fields.Many2one('res.users', string='Technician')

    employee_id = fields.Many2one('hr.employee', string='Employee')
    
    status = fields.Selection([('assigned', 'Assigned'), ('returned', 'Returned')], string='Status', default='assigned')
    return_date = fields.Date(string='Return Date')
    return_condition = fields.Selection([('good', 'Good'), ('repairable', 'Repairable'), ('damaged', 'Damaged')], string='Return Condition')


    @api.onchange('status')
    def _onchange_status(self):
        if self.status == 'returned':
            self.return_date = fields.Date.today()

    @api.onchange('device_purpose')
    def _onchange_device_purpose(self):
        self.customer_id = False
        self.technician_id = False
        self.employee_id = False
        if self.device_purpose != 'for_customer':
            self.order_id = False


    @api.onchange('order_id')
    def onchange_order_id(self):
        if self.order_id:
            self.customer_id = self.order_id.partner_id
            self.sales_id = self.order_id.user_id


    def action_confirm(self):
        self.write({'state': 'done'})