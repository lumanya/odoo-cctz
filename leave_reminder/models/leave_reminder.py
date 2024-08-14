from odoo import models, api, fields
import datetime
import logging
from urllib.parse import urlencode

_logger = logging.getLogger(__name__)

class HrLeave(models.Model):
    _inherit = "hr.leave"

    last_reminder_time = fields.Datetime(string="Last Reminder Sent", default=lambda self: fields.Datetime.now())

    @api.model
    def send_leave_approval_reminder(self):
        _logger.info("Starting send_leave_approval_reminder")

        time_frame = datetime.timedelta(days=1)
        current_time = fields.Datetime.now()
        _logger.info("Current time: %s", current_time)

        if not self.last_reminder_time or current_time - self.last_reminder_time >= time_frame:
            pending_leaves = self.search([
                ("state", "=", "confirm"), 
                ("create_date", "<", current_time - time_frame)
            ])
            _logger.info("Found %d pending leave requests", len(pending_leaves))

            if pending_leaves:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                for leave in pending_leaves:
                    managers = leave.get_leave_managers()
                    for manager in managers:
                        if manager and manager.user_id and manager.user_id.partner_id.email:
                            url_action = self._create_url_action(base_url)
                            template = self.env.ref('leave_reminder.email_template_pending_leave_reminder')
                            template.with_context(
                                manager_name=manager.name,
                                url=url_action['url']
                            ).send_mail(leave.id, force_send=True)

                            _logger.info("Sent email for pending leave: %s to manager: %s", leave.name, manager.name)

                self.last_reminder_time = current_time
                _logger.info("Updated last_reminder_time to: %s", self.last_reminder_time)
            else:
                _logger.info("No pending leave requests found")

        _logger.info("send_leave_approval_reminder completed")

    def get_leave_managers(self):
        managers = []
        employee = self.employee_id

        if employee.parent_id:
            managers.append(employee.parent_id)

        if employee.department_id and employee.department_id.manager_id:
            managers.append(employee.department_id.manager_id)

        hr_manager = self.env['hr.employee'].search([('job_id.name', '=', 'Human Resource Manager')], limit=1)
        if hr_manager:
            managers.append(hr_manager)

        ceo = self.env['hr.employee'].search([('job_id.name', '=', 'CEO')], limit=1)
        if ceo:
            managers.append(ceo)

        return managers

    def _create_url_action(self, base_url):
        params = {
            'model': 'hr.leave',
            'view_type': 'list',
            'domain': "[('state', '=', 'confirm')]"
        }
        url = f"{base_url}/web?{urlencode(params)}"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new'
        }
