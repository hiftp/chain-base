# -*- coding: utf-8 -*-
{
    'name': 'Import account move from CSV or Excel File',
    'summary': '匯入excel至廠商帳單',
    'author': 'kulius',
    'category': 'account',
    'version': '15.0.0.1',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        "wizard/view_import_account_sale.xml",
    ],

    'installable': True,
    'application': True,
    "license": "AGPL-3",
}
