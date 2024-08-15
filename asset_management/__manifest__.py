{
    'name': "asset_management",
    'summary': "Asset Management",
    'sequence':15,
    'author': "Computer Center",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'mail', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/asset_sequence.xml',
        'views/asset_management_view.xml',
        'views/asset_move_view.xml',
        'views/templates.xml',
    ],
    "application": True,
    'installable': True,
     'license': 'AGPL-3',
}
