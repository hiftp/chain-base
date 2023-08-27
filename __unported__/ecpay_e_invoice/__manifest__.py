# -*- coding: utf-8 -*-
{
    'name': "ecpay_e_invoice",

    'summary': """
        綠界電子發票模組
        """,

    'description': """綠界電子發票模組""",

    'author': "at3226",
    'website': "mikuroda4402.github.io",
    'category': 'invoice',
    'version': '15.0.0.0',

    'depends': [
        'base',
        'sale',
        'account'
    ],

    'data': [
        'security/ir.model.access.csv',
        'data/demo.xml',

        'views/res_config_setting_view.xml',
        'views/uniform_invoice_view.xml',
        'views/menu.xml',
    ],
    "license": "AGPL-3",
}