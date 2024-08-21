from odoo import models, fields

class ProjectUpdate(models.Model):
    _inherit = 'project.update'

    status = fields.Selection(selection=[
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('off_track', 'Off Track'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
    ], string='Status', ondelete='set default')  # Add onDelete policy

    STATUS_COLOR = {
        'on_track':20,
        'at_risk':2,
        'off_track':23,
        'on_hold': 4,
        'to_define': 0,
        'completed':10,
    }

    color = fields.Integer(compute='_compute_color', string='Color')

    def _compute_color(self):
        for update in self:
            update.color = self.STATUS_COLOR.get(update.status, 10)   