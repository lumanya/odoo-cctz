from odoo import fields, api, models, _ 
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging
from odoo.http import request
from werkzeug.urls import url_encode

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'
   
    tender_submission_date = fields.Datetime(string="Tender Submission Date", tracking=True)
    deal_expiry_date = fields.Datetime(string="Deal Reg Expiry  Date")	
    pre_sale_id = fields.Many2one('res.users', string='Pre-Sales Person', tracking=True, required=True)
    account_manager = fields.Many2one('res.users', string='Account Manager', tracking=True, required=True)
    source = fields.Many2one('res.users', string='Opportunity Source', tracking=True, required=True)
    business_unit = fields.Many2one('crm.team', string="Business Unit", tracking=True, required=True)
    account_type_id = fields.Many2one('account.type', string='Account Type', tracking=True, required=False)
    purchase_time_frame_id = fields.Many2one('purchase.time', string="Purchase Time Frame", tracking=True)
    payment_terms_id = fields.Many2one('payment.terms', string="Payment Terms", tracking=True)
    status_id = fields.Many2one('crm.status', string="status", tracking=True)
    cc_margin = fields.Float(string="CC Margin", tracking=True)
    tender_status = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string="Tender Status", tracking=True)
    deal_reg = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string="Approved Deal Reg", tracking=True)

    renewable_subscription = fields.Selection([
        ('None', 'None'),
        ('First Time Opportunity With Subscription', 'First Time Opportunity With Subscription'),
        ('Re-occuring Opportunity With Subscription', 'Re-occuring Opportunity With Subscription')
    ], string="Renewable Subscription", tracking=True, required=True)
    cc_care = fields.Selection([
        ('None', 'None'),
        ('Breake and Fix', 'Break and Fix'),
        ('Install', 'Install'),
        ('Remote', 'Remote'),
        ('Managed', 'Managed')
    ], tracking=True)   
    region = fields.Selection([
        ('Dar es salaam', 'Dar es salaam'),
        ('Mwanza', 'Mwanza'),
        ('Arusha', 'Arusha'),
        ('Dodoma', 'Dodoma'),
        ('Zanzibar', 'Zanzibar')
     ], default="Dar es salaam", tracking=True) 

    tender_type = fields.Selection([
        ('Government', 'Government'),
        ('Corporate', 'Corporate')
    ], tracking=True, required=False)

    ranking = fields.Char(string='Ranking', help='Enter Ranking Eg. 2/53') 

    tender_visible = fields.Boolean(compute='_compute_tender_visibibilty')
    expiry_date_visible = fields.Boolean(compute='_compute_expiry_date_visible')
    is_renewal = fields.Boolean(default=False)
    reference_opportunity = fields.Many2one('crm.lead', string='Reference Opportunity', copy=False)
    renewal_product_refence = fields.Many2one('product.product', string='Reference Renwal Product', copy=False)
    invoice_number = fields.Char(string='Invoice Number')
    renewal_created = fields.Boolean(string='Renewal Created', default=False)    

    @api.model
    def generate_link(self):        
        base_url = request.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)

        return base_url      
        
    @api.depends('tender_status')
    def _compute_tender_visibibilty(self):
        for lead in self:
            if lead.tender_status == 'Yes':
                lead.tender_visible = True
            else:
                lead.tender_visible = False

    @api.depends('deal_reg')
    def _compute_expiry_date_visible(self):
        for lead in self:
            if lead.deal_reg == 'Yes':
                lead.expiry_date_visible = True
            else:
                lead.expiry_date_visible = False

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if self.stage_id and self.stage_id.name == 'None':
            self.account_manager = False

    @api.constrains('stage_id', 'account_manager')
    def _check_account_manager(self):
        for lead in self:
            if lead.stage_id and lead.stage_id.name != 'None' and not lead.account_manager:
                raise ValidationError("Account Manager is required when the stage is not None.")

    # Define method for sending email notification
    def send_email_to_user(self, user, template_id):
        template = self.env.ref(template_id)
        if template and user:
            if user.email:
                template.with_context(user=user).send_mail(self.ids, force_send=True, email_values={'email_to': user.email})
                _logger.info("Email sent to %s (%s)" % (user.name, user.email))
            else:
                _logger.warning("User %s does not have an email address." % user.name)
        else:
            if not template:
                _logger.warning("Email template '%s' not found." % template_id)
            if not user:
                _logger.warning("No user.")

  
  

 
    @api.constrains('stage_id', 'invoice_number')
    def _check_invoice_number(self):
        for lead in self:
            if lead.stage_id and lead.stage_id.name == 'Won' and not lead.invoice_number:
                raise ValidationError("Invoice number is required before you mark opportunity as won.")

   

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if self.stage_id and self.stage_id.name == 'None':
            self.source = False

  

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if self.stage_id and self.stage_id.name == 'None':
            self.renewable_subscription = False

    @api.constrains('stage_id', 'renewable_subscription')
    def _check_renewable_subscription(self):
        for lead in self:
            if lead.stage_id and lead.stage_id.name != 'None' and not lead.renewable_subscription:
                raise ValidationError("renewable_subscription is required when the stage is not None.")

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if self.stage_id and self.stage_id.name == 'None':
            self.business_unit = False

    @api.constrains('stage_id', 'business_unit')
    def _check_business_unit(self):
        for lead in self:
            if lead.stage_id and lead.stage_id.name != 'None' and not lead.business_unit:
                raise ValidationError("business unit is required when the stage is not None.")


    def _prepare_renewal_opportunity_vals(self, line):
        renewal_duration = int(line.renewal_duration)
        date_deadline = datetime.now() + timedelta(days=renewal_duration * 366)
        business_unit_id = line.business_unit_id
        renewal_product_refence = line.product_id.id

        expected_revenue = line.order_id.currency_id._convert(
            line.price_subtotal,
            self.company_currency,
            self.company_id,
            line.order_id.date_order or fields.Date.today()
        )

        return {
            'name': f'[Renewal] {line.name}',
            'tender_submission_date': self.tender_submission_date,
            'deal_expiry_date': self.deal_expiry_date,
            'pre_sale_id': self.pre_sale_id.id,
            'account_manager': self.account_manager.id,
            'source': self.source.id,
            'expected_revenue': expected_revenue,
            'business_unit': business_unit_id.id,
            'account_type_id': self.account_type_id.id,
            'purchase_time_frame_id': self.purchase_time_frame_id.id,
            'payment_terms_id': self.payment_terms_id.id,
            'status_id': self.status_id.id,
            'cc_margin': self.cc_margin,
            'tender_status': self.tender_status,
            'deal_reg': self.deal_reg,
            'renewable_subscription': self.renewable_subscription,
            'cc_care': self.cc_care,
            'region': self.region,
            'tender_type': self.tender_type,
            'ranking': self.ranking,
            'stage_id': self.env['crm.stage'].search([('name', '=', 'Renewal Lead')], limit=1).id,
            'partner_id': self.partner_id.id,
            'date_deadline': date_deadline.date(),
            'is_renewal': True,
            'reference_opportunity': self.id,
            'renewal_product_refence': renewal_product_refence
            # Add other fields as needed
        }

    def _check_and_create_renewal_opportunity(self):
        has_quotation = any(
            order.state in ['draft', 'sent', 'sale']
            for order in self.order_ids
        )

        if has_quotation:
            for order in self.order_ids:
                for line in order.order_line:
                    if line.is_renewal:
                        new_opportunity_vals = self._prepare_renewal_opportunity_vals(line)
                        new_opportunity = self.create(new_opportunity_vals)

    def _prepare_renewal_opportunity_vals_button(self, line):
        renewal_duration = int(line.renewal_duration)      
        business_unit_id = line.business_unit_id
        renewal_product_refence = line.product_id.id

        expected_revenue = line.order_id.currency_id._convert(
            line.price_subtotal,
            self.company_currency,
            self.company_id,
            line.order_id.date_order or fields.Date.today()
        )       

        return {
            'name': f'[Renewal] {line.name}',
            'tender_submission_date': self.tender_submission_date,
            'deal_expiry_date': self.deal_expiry_date,
            'pre_sale_id': self.pre_sale_id.id,
            'account_manager': self.account_manager.id,
            'source': self.source.id,
            'expected_revenue': expected_revenue,
            'business_unit': business_unit_id.id,
            'account_type_id': self.account_type_id.id,
            'purchase_time_frame_id': self.purchase_time_frame_id.id,
            'payment_terms_id': self.payment_terms_id.id,
            'status_id': self.status_id.id,
            'cc_margin': self.cc_margin,
            'tender_status': self.tender_status,
            'deal_reg': self.deal_reg,
            'renewable_subscription': self.renewable_subscription,
            'cc_care': self.cc_care,
            'region': self.region,
            'tender_type': self.tender_type,
            'ranking': self.ranking,
            'stage_id': self.env['crm.stage'].search([('name', '=', 'Renewal Lead')], limit=1).id,
            'partner_id': self.partner_id.id,
            'date_deadline': self.date_deadline + timedelta(days=renewal_duration * 366),
            'is_renewal': True,
            'reference_opportunity': self.id,
            'renewal_product_refence': renewal_product_refence
            # Add other fields as needed
        }

    
    def _check_and_create_renewal_opportunity_button(self):
        has_quotation = any(
            order.state in ['draft', 'sent', 'sale']
            for order in self.order_ids
        )

        if has_quotation:
            for order in self.order_ids:
                for line in order.order_line:
                    if line.is_renewal:
                        new_opportunity_vals = self._prepare_renewal_opportunity_vals_button(line)
                        new_opportunity = self.create(new_opportunity_vals)

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if self.stage_id and self.stage_id.name in ['Won', 'Lost']:
            self._check_and_create_renewal_opportunity()

    def action_set_won(self):
        result = super(CrmLead, self).action_set_won()
        self._check_and_create_renewal_opportunity()
        return result

    def action_set_lost(self, **additional_values):
        result = super(CrmLead, self).action_set_lost(**additional_values)
        self._check_and_create_renewal_opportunity()
        return result


    def action_create_renewal(self):
        self._check_and_create_renewal_opportunity_button()


   