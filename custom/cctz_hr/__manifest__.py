# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'CCTZ HR',
    'version': '-110',
    'category': 'Human Resources/Employees',
    'sequence': 15,
    'summary': 'CCTZ HR Module',
    'author': 'Nathaniel Anania',
    'description': "",
    'website': 'https://cctz.co.tz',
    'depends': [
        'base_setup',
        'mail',
        'hr',
        'hr_contract',
        'resource',
        'web',
    ],
    'data': [
        'views/hr_employee_form_inherit.xml',       
        'views/hr_contract_expiry_alert.xml',
        'views/hr_contract_expiry_alert _probation.xml',
        'views/hr_contract_form_inherit.xml',
        'data/mail_template.xml',
        'data/mail_template_probation.xml',
        'views/hr_leave_inherit_view.xml',
         
       
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False
}