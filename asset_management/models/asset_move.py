from odoo import api, models, fields,_

class asset_move(models.Model):
    _name = 'asset.move'
    _inherit = 'mail.thread'
    _description = 'Asset Move'

    asset_id = fields.Many2one(
        'asset.registration', 
        string='Asset', 
        required=True,
    )

    move_date = fields.Date(string='Movement Date', required=True, default=fields.Date.context_today)

    assigned_to = fields.Selection([
        ('customer','Customer'), 
        ('technician', 'Technician'), 
        ('employee', 'Employee')
        
    ], string='Assign To', required=True)

    order_id = fields.Many2one(
        'sale.order',
        string='Order Number',
        required=False
    )

    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        domain= "[('customer_rank', '>', 0)]",
    )

    sales_id = fields.Many2one(
        'res.users',
        string='Sales Person'
    )

    technician_id = fields.Many2one(
        'res.users',
        string='Technician',
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
    )

    status = fields.Selection([
        ('assigned', 'assigned'),
        ('returned', 'returned'),
    ], string='Status', default='assigned')

    return_date = fields.Date(string='Return Date')
    return_condition = fields.Selection(
        [
            ('good', 'Good'),
            ('repairable', 'Repairable'),
            ('damaged', 'Damaged'),
        ], string='Return Condition'
    )

    description = fields.Char(string='More information' )

    @api.onchange('status')
    def _onchange_status(self):
        if self.status == 'returned':
            self.return_date = fields.Date.today()

    @api.onchange('assigned_to')
    def _onchange_assigned_to(self):
        self.customer_id = False
        self.technician_id = False
        self.employee_id = False
        if self.assigned_to != 'customer':
            self.order_id = False


    @api.onchange('order_id')
    def onchange_order_id(self):
        if self.order_id:
            self.customer_id = self.order_id.partner_id
            self.sales_id = self.order_id.user_id


    def action_confirm(self):
        self.write({'state': 'done'})