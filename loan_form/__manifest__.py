{
    "name": "Loan request",
    "author": "Ebenezer $ Rahim",
    "summary":"Loan request",
    'sequence': 15,
    "depends": [
       'base','mail'
    ],
    "data": [
        "security/ir.model.access.csv",
        'security/security.xml',
        "data/loan_sequence.xml",
        "data/mail_tempelate.xml",
        "views/loan_form.xml",
     
     
    ],
    'images': ['static/description/banner.png'],
    "application": True,
    'installable': True,
    'license': 'AGPL-3',
}
