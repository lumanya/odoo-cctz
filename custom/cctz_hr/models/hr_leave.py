from odoo import models, fields, api, _
from odoo.exceptions import UserError
from werkzeug.urls import url_encode
from odoo.http import request
import logging


_logger = logging.getLogger(__name__)


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    backup_id = fields.Many2one('res.users', string='Backup Person', required=True, store=True,)  
    return_date = fields.Date(string='Return Date')  
    general_manager_id = fields.Many2one('hr.employee', compute='_compute_manager')


    @api.model
    def generate_link(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if base_url:
            return f"{base_url}/web#id={self.id}&view_type=form&model={self._name}"
        else:
            return False 

    def action_validate_with_email(self):
        # Call the original action_validate function to keep the existing functionality
        res = super(HrLeave, self).action_validate()

        # Send notification emails when the leave request is validated
        self.send_email_notification('General Manager', 'cctz_hr.leave_notification')
        self.send_email_notification('Service Desk', 'cctz_hr.leave_notification_servicedesk')

        return res


    def send_email_notification(self, recipient_type, template_ref):
        _logger.info(f"Sending email notification to {recipient_type}")
        if recipient_type == 'General Manager':
            recipient_email = self.general_manager_id.work_email
        elif recipient_type == 'Service Desk':
            recipient_email = 'servicedesk@cctz.co.tz'
        
        if not recipient_email:
            _logger.warning(f"{recipient_type} email not found.")
            return
        
        template = self.env.ref(template_ref)
        if template:          
            template.send_mail(
                self.id,
                force_send=True,
                email_values={'email_to': recipient_email}
            )          
        else:
            _logger.warning(f"Email template '{template_ref}' not found.")


    def _compute_manager(self):      
        for leave in self:
            manager = self.env['hr.employee'].search([('job_title', '=', 'General Manager')], limit=1)           
            leave.general_manager_id = manager.id




