from odoo import models, fields

class ProjectUpdate(models.Model):
    _inherit = 'project.update'

    status = fields.Selection(selection=[
        ('on_track', 'Completed'),
        ('at_risk', 'In-Progress'),  
    ], string='Status')

    # Mapping statuses to colors
    STATUS_COLOR = {
        'on_track': 20,  # Color code for 'Completed'
        'at_risk': 2,    # Color code for 'In-Progress'
    }

    # Color field to be computed based on the status
    color = fields.Integer(compute='_compute_color', string='Color')

    # Compute method to assign the correct color based on the status
    def _compute_color(self):
        for update in self:
            # Get the color corresponding to the status, default to 10 if not found
            update.color = self.STATUS_COLOR.get(update.status, 10)
