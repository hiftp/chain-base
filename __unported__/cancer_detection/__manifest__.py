# -*- coding: utf-8 -*-
{
    'name': "Cancer Detection",
    'summary': """This module is used to detect cancer.""",
    'description': """This module is used to detect cancer""",
    'author': "AliFaleh",
    'website': "http://www.yourcompany.com",
    'category': 'Cancer',
    'version': '13.0',
    'depends': ['base', 'contacts', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/record_rules.xml',
        'views/partner_scan.xml',
        'views/res_partner.xml',
        'views/res_users.xml',
    ],
    'application': True,
    'license': 'Other OSI approved licence',  # MulanPubL-2.0
}
