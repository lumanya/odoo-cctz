from queue import Full
from odoo import models, fields, api,_
import logging

_logger = logging.getLogger(__name__)
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

    move_number = fields.Char(string='Move Number', copy=False, readonly=True, required=True, store=True)

    asset_name = fields.Many2one(related='asset_id.asset_name_id', string='Asset Name', readonly=True, required=True)

    date = fields.Date(related='asset_id.date', string='Receiving Date', readonly=True)

    device_purpose = fields.Selection(related='asset_id.device_purpose', string='Asset Type', readonly=True)
    
    warranty_start_date_move = fields.Date(related='asset_id.warranty_start_date', string='Warranty Start Date', readonly=True)

    warranty_end_date_move = fields.Date(related='asset_id.warranty_end_date', string='Warranty End Date', readonly=True)
    
    supplier_id = fields.Many2one(related='asset_id.supplier_id', string='Supplier Name', readonly=True)

    device_part_number = fields.Char(related='asset_id.device_part_number', string='Serial Number/Part Number', readonly=True, store=True)

    quantity = fields.Integer(related='asset_id.quantity', string='Quantity', readonly=True, store=True)

    description = fields.Text(related='asset_id.description', string='Description', readonly=True, store=True)

    display_description = fields.Char(string='Description', compute='_compute_display_description')
    
    move_date = fields.Date(string='Movement Date', required=True)

    technician_id_move = fields.Many2one('res.users', string='Technician')

    employee_id_move = fields.Many2one('hr.employee', string='Employee')
    
    customer_move_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    
    status_tech = fields.Selection([('in_use', 'In Use'), ('available', 'Available')], string='Availability', default ='available', readonly=True)
    
    status = fields.Selection([('assigned', 'Assigned'), ('returned','Returned')], string='Status', default = 'assigned', required=True)
    
    return_date = fields.Date(string='Return Date')

    return_condition = fields.Selection([('good', 'Good'), ('repairable', 'Repairable'), ('damaged', 'Damaged')], string='Device Condition', default='good',readonly=True)
    
    invoice_number_move = fields.Char(string='Invoice Number')
    
    asset_move_history_ids = fields.One2many('asset.move.history', 'asset_move_id', string='History')
    
    asset_move_employee_ids = fields.One2many('asset.move.employee', 'asset_employee_id', string='Employee History')
    
    current_location_move = fields.Many2one('hr.department', related='asset_id.current_location', string='Current Location', readonly=True, store=True)
    
    manager_id_move = fields.Many2one('hr.employee', string='Owner', readonly=True)
    
    asset_oprational_move_ids = fields.One2many('asset.operational.move', 'asset_operational_id', string='Operational Asset Asset' )
    
    state_move = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('rejected','Rejected')
        ], string='Status', default='draft', track_visibility='onchange', tracking=True, readonly=True)
    
    
    def action_approve(self):
        self.state_move = 'approved'      
        for operational_move in self.asset_oprational_move_ids:
            if operational_move.state == 'to_approve':
                operational_move.state = 'approved'
                operational_move.action_send_accepted_email()
            operational_move.update_asset_location_if_approved()
            
                
    def action_reject(self):
        self.state_move = 'rejected'
        for operational_move in self.asset_oprational_move_ids:
            if operational_move.state == 'to_approve':
                operational_move.state = 'rejected'
                operational_move.action_send_rejected_email()
            _logger.info(f"Asset move rejected; location update skipped")
            

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
        self.technician_id_move = False
        self.employee_id_move = False
      
        
    @api.depends('description')
    def _compute_display_description(self):
        for record in self:
            record.display_description = record.description if record.description else 'There is no description'


    def action_confirm(self):
        self.write({'state': 'done'})  