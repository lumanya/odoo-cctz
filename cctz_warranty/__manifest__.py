# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Warrant Plus',
    'version': '-110',
    'category': 'Sales/Warranty',
    'sequence': 15,
    'summary': 'Warranty Plus',
    'author': 'Nathaniel Anania',
    'description': "",
    'website': 'https://cctz.co.tz',
    'depends': [
        'base_setup',
        'sales_team',
        'mail',
        'calendar',
        'resource',  
        'utm',
        'web_tour',
        'contacts',
        'digest',
        'phone_validation',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ir_sequence_data.xml',
        'data/email_reminder_template.xml',
        'data/email_template.xml',
        'data/email_reminder_cron.xml',
        'reports/warranty_plus_template.xml',
        'reports/warranty_plus_reports.xml',           

        'views/warranty_request_views.xml',
       
        'views/hpe_support.xml',
        'views/warranty_menu.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False
}