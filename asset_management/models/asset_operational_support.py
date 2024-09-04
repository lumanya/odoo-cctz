from odoo import api, models, fields,_
from odoo.exceptions import ValidationError

class AssetOperationalMove(models.Model):
    _name = 'asset.operational.move'
    _description = 'Asset Operational Move'
    _order = 'create_date desc'

    asset_operational_id = fields.Many2one(
        'asset.move', 
        string='Asset Move',
        required=True,
        ondelete='cascade',  # Ensure history records are deleted if the related asset move is deleted
    )
    
    from_department = fields.Char(
        string='From Department',
        readonly=True,
        store=True,
    )
    
    to_department = fields.Char(
        string='To Department',
        required=True,
    )
    
    movement_date = fields.Date(
        string='Movement Date',
        required=True,
    )
    
    device_condition = fields.Selection([
        ('good', 'Good'),
        ('bad', 'Bad'),
        ('repairable', 'Repairable')
    ], string='Device Condition', required=True)
    
    @api.model
    def create(self, vals):
        asset_move = self.env['asset.move'].browse(vals['asset_operational_id'])
        vals['from_department'] = asset_move.current_location_move
        
        record = super(AssetOperationalMove, self).create(vals)
        
        if record.to_department:
            record.asset_operational_id.asset_id.current_location = record.to_department
        else:
            raise ValidationError(_('Please specify which Department asset is moved'))
        return record
    