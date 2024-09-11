from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class asset_registration(models.Model):
    _name = 'feedback.custom'
    _inherit = 'mail.thread'
    _description = 'feedback'
    
    customer_id = fields.Many2one('res.partner', string='Customer', domain="[('customer_rank', '>', 0)]")
    
    feedback_type = fields.Selection([
        ('notes', 'Notes'),
        ('meeting_minutes', 'Meeting Minutes'),
        ('to_do', 'To do'),
    ], string='Feedback Type')
    
    rating = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ], string='Ratings')
    
    comments = fields.Text(string='Comments')
    status = fields.Char(string='Status')
    submission_date = fields.Date(string='Submission Date', default=fields.Date.context_today)
    description = fields.Text(string="Description")