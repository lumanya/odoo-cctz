from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ContractInherit(models.Model):
    _inherit = 'hr.contract'

    probation_end_date = fields.Date(string='Probation End Date')

    attachment_ids = fields.One2many('ir.attachment', 'res_id', string="Attachments")

    # To display in form view
    supported_attachment_ids = fields.Many2many(
        'ir.attachment', string="Attach File", compute='_compute_supported_attachment_ids',
        inverse='_inverse_supported_attachment_ids')
    supported_attachment_ids_count = fields.Integer(compute='_compute_supported_attachment_ids')


    @api.depends('attachment_ids')
    def _compute_supported_attachment_ids(self):
        for contract in self:
            contract.supported_attachment_ids = contract.attachment_ids
            contract.supported_attachment_ids_count = len(contract.attachment_ids.ids)

    def _inverse_supported_attachment_ids(self):
        for contract in self:
            contract.attachment_ids = contract.supported_attachment_ids

    @api.model
    def contract_probation_expiry_alert(self):
        # Find contracts that are about to expire in the next 30 days
        contracts_to_alert = self.search([
            ('state', '=', 'open'),
            ('probation_end_date', '>=', fields.Date.today()),
            ('probation_end_date', '<=', fields.Date.today() + timedelta(days=45)),
        ])

        # Load the email template
        template = self.env.ref('cctz_hr.mail_template_contract_probation_expiery_alert', raise_if_not_found=False)
        if not template:
            raise UserError(_("Email template 'mail_template_contract_probation_expiery_alert' not found. Please create the template."))

        for contract in contracts_to_alert:
            # Check if the contract has an HR responsible with an email address
            if contract.hr_responsible_id and contract.hr_responsible_id.email:
                template.send_mail(contract.id, force_send=True)


    @api.model
    def contract_expiry_alert(self):
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

  
