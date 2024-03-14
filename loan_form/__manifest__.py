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
        "views/loan_form.xml",
    ],
    "application": True,
    'installable': True,
    'license': 'AGPL-3',
}
