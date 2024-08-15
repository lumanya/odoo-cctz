# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.http import request
import logging


_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    lpo_number = fields.Char(string='LPO Number')

    account_manager_id = fields.Many2one(
        'res.users',  # Target model
        string='Account Manager',
        related='opportunity_id.account_manager',  # Link to the account_manager field in crm.lead
        store=True,  # Store the value in the database for efficient retrieval
        readonly=True
    )
    opportunity_source_id = fields.Many2one(
        'res.users',  # Target model
        string='Opportunity Source',
        related='opportunity_id.source',  # Link to the account_manager field in crm.lead
        store=True,  # Store the value in the database for efficient retrieval
        readonly=True
    )

    pre_sale_id = fields.Many2one(
        'res.users',  # Target model
        string='Pre-Sales Person',
        related='opportunity_id.pre_sale_id',  # Link to the account_manager field in crm.lead
        store=True,  # Store the value in the database for efficient retrieval
        readonly=True
    )
    procurment_manager_id = fields.Many2one('hr.employee', compute='_compute_procurment_manager')

    @api.model
    def generate_link(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if base_url:
            return f"{base_url}/web#id={self.id}&view_type=form&model={self._name}"
        else:
            return False    

    def action_confirm_email(self):
        # call the original action_confirm function to keep existing functionality
        sale = super(SaleOrder, self).action_confirm()

        self.send_email_notification()
        
        return sale

    def send_email_notification(self):
        procurment_manager = self.env['hr.employee'].search([('job_title', '=', 'Head of Procurement & Accountant')], limit=1)
        template = self.env.ref('custom_cctz.email_template_procurment_manager_approver')

        if procurment_manager and template:
            if procurment_manager.work_email:
                template.send_mail(self.id, force_send=True, email_values={'email_to': 'shaibu.lumanya@cctz.co.tz'})
                _logger.info('Email sent to procurement manager.')
            else:
                _logger.warning('No work email found for procurement manager.')
        else:
            _logger.error('No procurement manager or email template found.')  

    def _compute_procurment_manager(self):      
        for leave in self:
            manager = self.env['hr.employee'].search([('job_title', '=', 'Head of Procurement & Accountant')], limit=1)           
            leave.procurment_manager_id = manager.id      
      



   

