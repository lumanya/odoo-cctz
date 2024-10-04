from odoo import models, fields, api, _
class ProjectProject(models.Model):
    _inherit = 'project.project'

    last_update_status = fields.Selection(
        selection=[
            ('on_track', 'Completed'),
            ('at_risk', 'In-Progress'),
        ],
        string="Last Update Status"
    )

    STATUS_COLOR = {
        'on_track': 20,
        'at_risk': 2,
    }

    last_update_color = fields.Integer(compute='_compute_last_update_color', string='Last Update Color')

    def _compute_last_update_color(self):
        for project in self:
            project.last_update_color = self.STATUS_COLOR.get(project.last_update_status, 0)

    @api.model
    def create(self, vals):
        project = super(ProjectProject, self).create(vals)
        # Add default stages to new projects
        default_stages = [
            {'name': 'Initiation'},
            {'name': 'Planning'},
            {'name': 'Procurement'},
            {'name': 'Inspection & Delivery'},
            {'name': 'Design'},
            {'name': 'Kick-off meeting'},
            {'name': 'Deployment'},
            {'name': 'Risk'},
            {'name': 'Sign-off'},
            {'name': 'Training'},
            {'name': 'Payment'},
            {'name': 'Postmortem'},
        ]
        for stage in default_stages:
            project.type_ids += self.env['project.task.type'].sudo().create(stage)
        return project

    def name_create(self, name):
        res = super().name_create(name)
        if res:
            # Create a default stage `New` for projects created on the fly
            self.browse(res[0]).type_ids += self.env['project.task.type'].sudo().create({'name': _('New')})
        return res
