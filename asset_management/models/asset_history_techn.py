from odoo import api, models, fields
from odoo.exceptions import ValidationError

class AssetMoveHistory(models.Model):
    _name = 'asset.move.history'
    _description = 'Asset Move History'
    _order = 'create_date desc'

    asset_move_id = fields.Many2one(
        'asset.move', 
        string='Asset Move',
        required=True,
        ondelete='cascade',  # Ensure history records are deleted if the related asset move is deleted
    )
    
    technician_id = fields.Many2one(
        'res.users',  # Assuming technicians are represented by user records
        string='Technician',
        required=True
    )
   
    employee_id = fields.Many2one(
        'hr.employee', 
        string='Employee',
        
    )
 
    start_date = fields.Date(
        string='Taken Date',

        required=True
    )
    
    end_date = fields.Date(
        
        string='Return Date'
        
    )
    
    return_condition_tech = fields.Selection([('good', 'Good'), ('repairable', 'Repairable'), ('damaged', 'Damaged')], string='Return Condition')
    
    status = fields.Selection([('assigned', 'Assigned'), ('returned','Returned')], string='Status')
   
    @api.model
    def create(self, vals):
        asset_move = self.env['asset.move'].browse(vals['asset_move_id'])
        if asset_move.status_tech == 'in_use':
            raise ValidationError("The asset is currently in use by another technician. It cannot be reassigned untill is returned")
        
        record = super(AssetMoveHistory, self).create(vals)
        
        asset_move.status_tech = 'in_use' if not record.end_date else 'available' 
        
        return record
    
    def write(self, vals):
        res = super(AssetMoveHistory, self).write(vals)
        for record in self:
            if 'end_date' in vals:
                record.asset_move_id.status_tech = 'available'
            elif 'start_date' in vals and not record.end_date:
                record.asset_move_id.status_tech = 'in_use'
        return res
    
    # Optionally, add a computed field or method to display additional information or handle specific logic