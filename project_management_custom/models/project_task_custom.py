from odoo import models, fields, api, _

class ProjectTaskTypeCustom(models.Model):
    _inherit = 'project.task.type'
    
    legend_done = fields.Char(
        'Green Kanban Label', default=lambda s: _('Completed'), translate=True, required=True)
    legend_normal = fields.Char(
        'Grey Kanban Label', default=lambda s: _('In Progress'), translate=True, required=True)
    
    
    
class ProjectTaskCustom(models.Model):
    _inherit = 'project.task'

    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Completed'),
        ], string='Status', copy=False, default='normal', required=True, compute='_compute_kanban_state', readonly=False, store=True)
    
    kanban_state_label = fields.Char(compute='_compute_kanban_state_label', string='Kanban State Label', tracking=True, task_dependency_tracking=True)
    
    
    @api.depends('stage_id', 'project_id')
    def _compute_kanban_state(self):
        self.kanban_state = 'normal'
        
    def _compute_kanban_state_label(self):
        for task in self:
            if task.kanban_state == 'normal':
                task.kanban_state_label = task.legend_normal
            else:
                task.kanban_state_label = task.legend_done