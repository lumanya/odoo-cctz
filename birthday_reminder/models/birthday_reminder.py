from odoo import fields, models, api
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)

class HrEmployeeBirthday(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def send_birthday_reminders(self):
        today = fields.Date.today()
        start_date = today + timedelta(days=1)
        end_date = today + timedelta(days=3)
        _logger.info(f"Checking birthdays between {start_date} and {end_date}")
        
        upcoming_birthdays = self.search([('birthday', '!=', False)])
        print(f'Upcoming birthdays {upcoming_birthdays}')
        for employee in upcoming_birthdays:
            birthday = fields.Date.from_string(employee.birthday)
            birthday_this_year = birthday.replace(year=today.year)
            if start_date <= birthday_this_year <= end_date:
                _logger.info(f"Employee {employee.name} has a birthday on {birthday}")
                hr_department = self.env['hr.employee'].search([('job_title', '=', 'Human Resource Manager')], limit=1)
                if hr_department:
                    _logger.info(f"Sending email to HR manager: {hr_department.work_email}")
                    template = self.env.ref('birthday_reminder.birthday_reminder_email_template')
                    template.send_mail(employee.id, force_send=True, email_values={'email_to': hr_department.work_email})
                else:
                    _logger.warning("No HR manager found")
