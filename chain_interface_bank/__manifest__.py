# -*- coding: utf-8 -*-

{
    'name': '鲜生活银企直联模块',
    'summary': """
    本模块将实现odoo与鲜生活内部银行和农业银行的链接接口。提供oa将收付单据金额与银行直接通信的功能
    """,
    'description': """
    具体功能调用请阅读接口文档（doc目录下）    
    """,
    'author': 'Inspur SuXueFeng',
    'website': "https://www.sxfblog.com",
    'category': 'interface',
    'version': '1.0',
    'depends': ['base',
                ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'data': [
        'security/ir.model.access.csv',
        'groups/interface_bank_groups.xml',
        'views/menu.xml',
        'views/bank_setting.xml',
        'views/payment_commit.xml',
        'views/caiqitong_objects.xml',
        'views/payment.xml',
        'views/bank_public_accounts.xml',
        'views/inherit_objects.xml',
        'views/interface_bank_log.xml',
        'views/search_result.xml',
        'views/dash_board.xml',
        'data/from_number.xml',
        'data/default_data.xml',
        'views/abc_bank/search_function.xml',
        'views/abc_bank/abc_payment.xml',
        'views/abc_bank/abc_config.xml',
    ],
    # 'qweb': [
    #     'static/src/xml/*.xml',
        # 'static/src/xml/search_account_bal.xml',
        # 'static/src/xml/dash_board.xml',
        # 'static/src/xml/abc_search_function.xml',
    # ],

}
