# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (C) 2017-now  yuanchih-consult.com :chingyun@yuanchih-consult.com

{
    'name': '元復客製模組',
    'version': '1.0',
    'category': 'Accounting/Localizations',
    'author': ['https://eoffice.alltop.com.tw/'],

    'website': 'https://eoffice.alltop.com.tw/',
    'description': """
元復醫院客製模組
    """,
    'depends': ['base', 'account'],
    'data': [
        'views/res_partner.xml',
        'views/account_account_view.xml',
        'views/account_move_views.xml',
    ],
    "license": "AGPL-3",
}
