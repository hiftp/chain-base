# -*- coding: utf-8 -*-
{
    'name': "Utilities: Redis Session Storage",

    'summary': """
       This module is used to change the way odoo store the user session. The Session will be store in Redis Database.""",

    'description': """
        This module is used to change the way odoo store the user session. 
        The Session will be store in Redis Database instead of local file system.
    """,

    'author': "The Bean Family,Xiaxiaozheng",
    'maintainer': "The Bean Family",
    'license': "LGPL-3",
    'category': 'Bean Family Modules/Utilities',
    'version': '16.0.0.2',
    'website': "https://www.thebeanfamily.org",
    'support': 'community@thebeanfamily.org',
    "application": True,
    "installable": True,
    'images': ['static/description/image.png'],

    # any module necessary for this one to work correctly
    'depends': ['base'],
}
