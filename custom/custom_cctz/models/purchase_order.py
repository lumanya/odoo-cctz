from odoo import api, fields, models
from datetime import timedelta
import logging


_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    sap_po_number = fields.Char(string='PO Number(SAP)')
    salesperson = fields.Many2one('res.users', string='Salesperson', compute='_compute_salesperson', store=True)

    @api.model
    def generate_link(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if base_url:
            return f"{base_url}/web#id={self.id}&view_type=form&model={self._name}"
        else:
            return False  

    @api.depends('origin')
    def _compute_salesperson(self):
        for order in self:
            if order.origin:
                sale_order = self.env['sale.order'].search([('name', '=', order.origin)], limit=1)
                if sale_order:
                    order.salesperson = sale_order.user_id

    def send_email_notification(self):
        # Get the salesperson who generated the purchase order
        salesperson = self.env['sale.order'].search([('name', '=', self.origin)]).user_id

        # Get the email address of the salesperson
        salesperson_email = salesperson.partner_id.email

        # Compose the email
        template = self.env.ref('custom_cctz.email_template_purchase_order_confirmation')

        if template:
            if salesperson_email:
                template.send_mail(self.id, force_send=True, email_values={'email_to': salesperson_email})
                _logger.info('Email sent to salesperson.')
            else:
                _logger.warning('No work email found  salesperson.')
        else:
            _logger.error('No email template found.')  
      

    def button_confirm_email(self):
        # Call the original button_confirm function to keep existing functionality
        purchase_order = super(PurchaseOrder, self).button_confirm()

        # Send email notification
        self.send_email_notification()

        # Send email notification to person handling receipts
        self.send_receipt_notification()
        
        return purchase_order

    def send_receipt_notification(self):
        # Get the salesperson who generated the purchase order
        salesperson = self.env['sale.order'].search([('name', '=', self.origin)]).user_id

        # Get the email address of the salesperson
        salesperson_email = salesperson.partner_id.email

        # Compose the email
        template = self.env.ref('custom_cctz.email_template_receipt_notification')

        if template:
            if salesperson_email:
                template.send_mail(self.id, force_send=True, email_values={'email_to': salesperson_email})
                _logger.info('Email sent to salesperson.')
            else:
                _logger.warning('No work email found  salesperson.')
        else:
            _logger.error('No email template found.') 


    def send_delayed_confirmation_email(self, order_ids):
        # Send escalation email to the general manager for delayed confirmations
        template = self.env.ref('custom_cctz.email_template_delayed_confirmation')
        general_manager = self.env['hr.employee'].search([('job_title', '=', 'General Manager')], limit=1)
        if template and general_manager:
            for order_id in order_ids:
                template.send_mail(order_id, force_send=True, email_values={'email_to': general_manager.work_email})
            _logger.info('Escalation email sent to the general manager.')
        else:
            _logger.error('Email template or general manager email address not found.') 

    def check_delayed_confirmations(self):
        delay_threshold = timedelta(days=1)
        today = fields.Date.today()
        orders = self.search([('state', '=', 'draft'), ('date_order', '<=', today - delay_threshold)])
        if orders:
            self.send_delayed_confirmation_email(orders.ids)

   
    
