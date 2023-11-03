# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (C) 2018-now  jeffery9@gmail.com

{
    'name': 'China - City Data',
    'version': '16.0.1.8.3',
    'icon': '/l10n_cn/static/description/icon.png',
    'category': 'Accounting/Localizations',
    'author': 'xiaxiaozheng',
    "excludes": ["l10n_cn_city"],
    'description': """
Includes the following data for the Chinese localization
========================================================

City Data/城市数据

版本历史

2023年10月1日 升级到1.8.2 
    修正地区数据
    增加公司地址自动引用国内地区行政数据


    """,
    'depends': [
        # 'l10n_cn_chain',
        # 'l10n_cn_standard_latest_chain',
        'base_address_extended',
    ],
    'data': [
        'data/res_city_data.xml',
        'data/res_country_data.xml',
        'views/res_partner_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
}
