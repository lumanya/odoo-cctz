from odoo import api, fields, models
from datetime import timedelta

class OpportunityReminder(models.Model):
    _name = 'opportunity.reminder'
    _description = 'Opportunity Reminder'

    opportunity_id = fields.Many2one('crm.lead', string='Opportunity')
    user_id = fields.Many2one('res.users', string='Salesperson')

    @api.model
    def check_opportunities_and_send_reminders(self):
        # Logic to check for upcoming opportunities and send reminders
        # This method will be called by the scheduled action
        # You can use the Odoo ORM to query and process data
        # Example: Find opportunities with date_deadline within the next 30 days and is_renewal set to True
        today = fields.Date.today()
        upcoming_opportunities = self.env['crm.lead'].search([
            ('date_deadline', '>', today),
            ('date_deadline', '<=', today + timedelta(days=30)),
            ('stage_id', 'not in', [stage_id_for_closed, stage_id_for_won]),
            ('is_renewal', '=', True)
        ])

        # Process each opportunity and send reminders
        for opportunity in upcoming_opportunities:
            # Get the salesperson for the opportunity (replace 'user_id' with the actual field name)
            salesperson = opportunity.user_id

            # Create a reminder record
            reminder = self.create({
                'opportunity_id': opportunity.id,
                'user_id': salesperson.id,
            })

            # Send email reminder using the Odoo email API
            template = self.env.ref('your_module.email_template_opportunity_reminder')
            template.send_mail(reminder.id, force_send=True)
