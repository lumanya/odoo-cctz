{
    "name": "Loan request",
    "author": "Ebenezer $ Rahim",
    "summary":"Loan request",
    "depends": [
       'base','mail'
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/loan_sequence.xml",
        "data/mail_tempelate.xml",
        "views/loan_form.xml",
        "views/loan_manage.xml",
    ],
    "application": True,
    'installable': True,
    'license': 'AGPL-3',
}
