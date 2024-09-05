from odoo import api, models, fields
from odoo.exceptions import ValidationError

class AssetMoveEmployee(models.Model):
    _name = 'asset.move.employee'
    _description = 'Asset Move History'
    _order = 'create_date desc'

    asset_employee_id = fields.Many2one(
        'asset.move', 
        string='Asset Move',
        required=True,
        ondelete='cascade',  # Ensure history records are deleted if the related asset move is deleted
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
    
    return_condition_tech = fields.Selection([('good', 'Good'), ('repairable', 'Repairable'), ('damaged', 'Damaged')], string='Asset Condition')
    
    status = fields.Selection([('assigned', 'Assigned'), ('returned','Returned')], string='Status')
   
    @api.model
    def create(self, vals):
        asset_move = self.env['asset.move'].browse(vals['asset_employee_id'])
        if asset_move.status_tech == 'in_use':
            raise ValidationError("The asset is currently in use by another employee. It cannot be reassigned untill is returned")
        
        record = super(AssetMoveEmployee, self).create(vals)
        
        asset_move.status_tech = 'in_use' if not record.end_date else 'available'
        
        if record.return_condition_tech:
            asset_move.return_condition = record.return_condition_tech 
        
        return record
    
    def write(self, vals):
        res = super(AssetMoveEmployee, self).write(vals)
        for record in self:
            if 'end_date' in vals:
                record.asset_employee_id.status_tech = 'available'
            elif 'start_date' in vals and not record.end_date:
                record.asset_employee_id.status_tech = 'in_use'
                
            if 'return_condition_tech' in vals:
                record.asset_employee_id.return_condition = vals['return_condition_tech']
        return res
    
 