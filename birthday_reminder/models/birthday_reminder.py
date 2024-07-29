from odoo import fields, models, api
from datetime import timedelta

class HrEmployeeBirthday(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def send_birthday_reminders(self):
        today = fields.Date.today()
        start_date = today + timedelta(days=1)
        end_date = today + timedelta(days=3)
        upcoming_birthdays = self.search([('birthday', '!=', False)])
        for employee in upcoming_birthdays:
            birthday = fields.Date.from_string(employee.birthday)
            if start_date <= birthday <= end_date:
                hr_department = self.env['hr.employee'].search([('job_title', '=', 'HR Manager')], limit=1)
                if hr_department:
                    template = self.env.ref('birthday_reminder.birthday_reminder_email_template')
                    template.send_mail(employee.id, force_send=True, email_values={'email_to': hr_department.work_email})
