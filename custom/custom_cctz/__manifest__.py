{
    'name': 'Custom CCTZ',
    'sequence': -110,
    'summary': 'Custom odoo app as per CCTZ requirements',
    'description': """Custom odoo app as per CCTZ requirements""",
    'category': 'CRM & Sales',
    'author': 'Nathaniel Anania',
    'maintainer': 'Nathaiel Anania',
    'website': 'https://churhcycodes.co.tz',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'crm',
        'contacts',
        'mail',
        'purchase',
        'sale_management',
        'stock'
       
        
    ],
    'data': [    
    'security/ir.model.access.csv',
    'data/mail_notification.xml',
    'data/scheduled_actions.xml',
    'views/crm_account_type.xml',
    'views/crm_payment_terms.xml',
    'views/crm_purchase_time_frame.xml',
    'views/crm_status.xml',
    'views/crm_inherit_crm_lead_view.xml',
    'views/product_manufacuture.xml',
    'views/product_inherit_product_template.xml',
    'views/sector_info.xml',
    'views/market_category.xml',
    'views/customer_type.xml',
    'views/inherit_res_partner.xml',
    'views/sale_order_view.xml', 
    'views/sale_order_line_view.xml',
    'views/stock_picking_inherit.xml',
    'views/stock_picking.xml',  
    'views/purchase_order_inherit.xml',
    'report/sale_order_template.xml',
    

  
       
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'autoinstall': False,
   
    }
