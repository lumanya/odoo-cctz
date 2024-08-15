{
    "name": "Change Request form",
    "author": "Ebenezer $ Rahim",
    "summary":" Change Request form ",
    "depends": [
       'base','hr','mail'
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/data_file.xml",
        "data/mail_tempelate.xml",
        "views/change_request.xml",
        "views/request_manage.xml",
    ],
    "application": True,
    'installable': True,
    'license': 'AGPL-3',
}