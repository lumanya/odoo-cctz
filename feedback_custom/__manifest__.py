{
    'name': "Customer Feedback",
    'summary': "Customer Feedback",
    'sequence':15,
    'author': "Computer Center",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'mail', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/feedback.xml',
    ],
    "application": True,
    'installable': True,
     'license': 'AGPL-3',
}
