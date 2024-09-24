from odoo import api, models, fields,_
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

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
    
    from_department = fields.Many2one(
        'hr.department',
        string='From Department',
        readonly=True,
        store=True,
    )
    
    to_department = fields.Many2one(
        'hr.department',
        string='To Department',
        required=True,
    )
    
    movement_date = fields.Date(
        string='Movement Date',
        required=True,
    )
    
    device_condition = fields.Selection([
        ('good', 'Good'),
        ('damaged', 'Damaged'),
        ('repairable', 'Repairable')
    ], string='Device Condition', required=True)
    
    menu_id = fields.Integer(string='Menu ID')
    action_id = fields.Integer(string='Action ID')
    
    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('to_approve', 'To Approve'),
    #     ('second_approval', 'Second Approval'),
    #     ('third_approval', 'Third Approval'),
    #     ('approved', 'Approved'),
    #     ('rejected','Rejected')
    #     ], string='Status', default='draft', track_visibility='onchange', tracking=True)
    
    def action_approve(self):
        # self.state = 'second_approval'      
        self.send_email_to_head_of_department()

    def generate_link(self, menu_id, action_id, create_uid): 
        _logger.warning(f"create_uid: {create_uid}, menu_id: {menu_id}, action_id: {action_id}")
        
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if base_url:
            return f"{base_url}/web#id={self.id}&view_type=form&model={self._name}"
        else:
            return "#"
    
    def get_department_managers(self):
        department = self.from_department
        if department:
            manager_ids = department.manager_id.user_id
            return manager_ids
        else:
            return []

    
    def send_email_to_head_of_department(self):
    # Ensure from_department is not empty
        if not self.from_department:
            _logger.warning("No department set for asset movement.")
            return
        
        # Fetch the manager user for the department
        manager_user = self.from_department.manager_id.user_id if self.from_department.manager_id else None
        
        if manager_user:
            template = self.env.ref('asset_management.asset_movement_approver', raise_if_not_found=False)
            
            if template:
                # Check if the manager has an email
                if manager_user.work_email:
                    # Send the email to the department head
                    template.with_context(user=manager_user).send_mail(
                        self.id, 
                        force_send=True, 
                        email_values={'email_to': manager_user.work_email}
                    )
                    _logger.info(f"Email sent to {manager_user.name} ({manager_user.work_email})")
                else:
                    _logger.warning(f"Manager {manager_user.name} does not have an email address.")
            else:
                _logger.warning("Email template 'asset_management.asset_movement_approver' not found.")
        else:
            _logger.warning("No manager of department found.")


    
    @api.model
    def create(self, vals):
        asset_move = self.env['asset.move'].browse(vals['asset_operational_id'])
        
        # Debugging log to ensure asset_move is retrieved
        _logger.info(f"Asset Move Retrieved: {asset_move}")
        
        last_move = self.search([('asset_operational_id', '=', asset_move.id)], order="create_date desc", limit=1)
        
        if last_move and last_move.device_condition == 'damaged':
            raise ValidationError(_('You cannot move a damaged asset'))
        
        # Assign from_department based on the current location of the asset
        if asset_move.current_location_move:
            vals['from_department'] = asset_move.current_location_move.id
            _logger.info(f"from_department set to: {vals['from_department']}")
        else:
            _logger.warning(f"Asset Move {asset_move.id} has no current location set.")
        
        record = super(AssetOperationalMove, self).create(vals)
        
        if record.to_department:
            record.asset_operational_id.asset_id.current_location = record.to_department.id
        else:
            raise ValidationError(_('Please specify which Department the asset is moved to'))
        
        if record.device_condition:
            asset_move.return_condition = record.device_condition 
        
        # Call send_email_to_head_of_department only if from_department is set
        if record.from_department:
            record.send_email_to_head_of_department()
        
        return record

    
    def write(self, vals):
        res = super(AssetOperationalMove, self).write(vals)
        for record in self:                
            if 'device_condition' in vals:
                record.asset_operational_id.return_condition = vals['device_condition']
        return res