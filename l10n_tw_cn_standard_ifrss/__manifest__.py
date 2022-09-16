# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (C) 2017-now  yuanchih-consult.com :chingyun@yuanchih-consult.com

{
    'name': '台灣常用會計科目與台灣財務報表結構(社區版)',
    'version': '1.1',
    'category': 'Localization',
    "license": "AGPL-3",
    'author': ['元植SmithLin'],
    'depends': ['base', 'account','l10n_tw_cn','accounting_pdf_reports'],
    'website': 'https://www.yuanchih-consult.com',
    'images': ['static/description/twbs-1.png'],
    'description': """

本模塊於14版進行功能任務調整，調整後提供以下功能：

*1.台灣常用會計項目匯入

*2.依odoo社區版財務報表模組(accounting_pdf_reports)為報表基礎呈現之台灣使用習慣財務報表結構

相關社區版財務報表運作方式、元植財務報表邏輯結構與年度結轉方式請詳以下文章：

https://www.yuanchih-consult.com/blog/odoo-1/post/odooodoo-15

odoo社區版系統上線前之基礎知識-odoo應用雲端課程說明：

https://www.yuanchih-consult.com/page/onlineclass

*本模組之使用請先下載並安裝l10n_tw_cn模組

https://github.com/Odoo-Taiwan/l10n_tw_cn

報表結構呈現範例：
<img src="general_ledger_filter.png">




*特別感謝：
★技術支援：新北工具人

★技術支援：先傑電腦

★技術支援：odooTaiwan曾大大


    """,

    'data': [
        'data/account_account_type_data.xml',
        'data/account.account.template.csv',
        'data/account.financial.report.csv',
        'data/account.financial.report.xml',
        'views/res.company.form.xml',
        'data/account.account.csv',
    ],
}
