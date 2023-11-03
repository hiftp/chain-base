 # -*- coding: utf-8 -*-
{
    'name': "Chinese font",

    'summary': """
        change defult font to nice chinese font""",

    'description': """
        Change the defult chinese font of the all interfaces with a beautiful one preferred by the Chinese user
 ,
    """,
    'author': "xiaxiaozheng",
    'website': "https://www.odoochain.com",
    'category': 'Localization',
    'version': '16.0.1.0.1',
    'depends': ['base', 'web'],
    'data': [],
    'assets': {
        # 这里是改样式，要 after处理
        'web.assets_common': [
            ('after', 'web_enterprise/static/src/webclient/home_menu/home_menu_background.scss',
             'xxz_chinese_font/static/src/scss/chinese_font.scss'),
            ('after', 'web/static/lib/jquery.ui/jquery-ui.css', 'xxz_chinese_font/static/src/css/web_style_cn.css'),

        ],
        'web.report_assets_common': [
            'xxz_chinese_font/static/src/css/pdf_style_cn.css',
            ],
    },
    "external_dependencies": {"python": [
        "baidu_aip",
        "baidu_aip_sdk",
        "tenacity",
        "wechatpy",
    ]},
    'license': 'LGPL-3',
    "installable": True,
    "auto_install": False,
    "application": True,
}
