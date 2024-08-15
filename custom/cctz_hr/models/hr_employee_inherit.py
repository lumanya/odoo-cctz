from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    tin_number = fields.Char(string='TIN Number', groups="hr.group_hr_user")


    @api.model
    def birthday_alert(self):
        # Find contracts that are about to expire in the next 30 days
        contracts_to_alert = self.search([
            ('state', '=', 'open'),
            ('date_end', '>=', fields.Date.today()),
            ('date_end', '<=', fields.Date.today() + timedelta(days=45)),
        ])

        # Load the email template
        template = self.env.ref('cctz_hr.mail_template_contract_expiery_alert', raise_if_not_found=False)
        if not template:
            raise UserError(_("Email template 'mail_template_contract_expiery_alert' not found. Please create the template."))

        for contract in contracts_to_alert:
            # Check if the contract has an HR responsible with an email address
            if contract.hr_responsible_id and contract.hr_responsible_id.email:
                template.send_mail(contract.id, force_send=True)


    