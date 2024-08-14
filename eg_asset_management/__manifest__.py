{
    'name': 'Asset Management',
    'version': '16.0.1.0.0',
    'category': 'Human Resources/Employees',
    'summary': 'Asset Management',
    'author': 'INKERP',
    'website': 'https://www.inkerp.com/',
    'depends': ['hr', 'mail'],
    
    'data': [
        'data/ir_sequence.xml',
        'views/asset_category_view.xml',
        'views/asset_detail_view.xml',
        'views/asset_location_view.xml',
        'views/asset_move_view.xml',
        'security/ir.model.access.csv',
    ],
    
    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
