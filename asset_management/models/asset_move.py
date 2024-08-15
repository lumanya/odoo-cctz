from odoo import api, models, fields,_

class asset_move(models.Model):
    _name = 'asset.move'
    _inherit = 'mail.thread'
    _description = 'Asset Move'

    asset_id = fields.Many2one(
        'asset.registration', 
        string='Asset', 
        required=True
    )

    move_date = fields.Date(string='Movement Date', required=True, default=fields.Date.today)

    assigned_to = fields.Selection([('customer','Customer'), ('technician', 'Technician')], string='Assign To', required=True)

    order_id = fields.Many2one(
        'sale.order',
        string='Order Number',
        domain= "[('partner_id', '=', customer_id)]",
        required=False
    )

    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        domain= "[('customer_rank', '>', 0)]",
    )

    technician_id = fields.Many2one(
        'res.partner',
        string='Technician',
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='State', default='draft')

    @api.onchange('assigned_to')
    def onchange_assigned_to(self):
        if self.assigned_to == 'customer':
            self.technician_id = False
        elif self.assigned_to == 'technician':
            self.customer_id = False

    @api.onchange('order_id')
    def onchange_order_id(self):
        if self.order_id:
            self.customer_id = self.order_id.partner_id

    def action_confirm(self):
        self.write({'state': 'done'})