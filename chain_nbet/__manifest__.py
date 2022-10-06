# -*- coding: utf-8 -*-
{
    'name': "NBET_Process",

    'summary': """
        This module was developed to streamline the financial/accounting app to fit NBET Specific Process""",

    'description': """
        to keep the financial module as close to what NBET is use to as possible
    """,

    'author': "Dominic Anyanna",
    'website': "http://www.pglnigeria.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'Other OSI approved licence',  # MulanPubL-2.0
    # any module necessary for this one to work correctly
    'depends': ['base',
                'mail',
                'account',
                # 'om_account_budget',
                'account_budget',
                'board',
                # 'om_account_asset',
                'account_asset',
                'web',
                'om_dynamic_reports',
                'recurring_payment_12',
                'ks_dashboard_ninja',
                'ebs_ocma',
                'accounting_pdf_reports',
                ],

    # always loaded
    'data': [
        'data/top.xml',
        'views/actions.xml',
        'data/groups.xml',
        'views/views.xml',
        'views/menu.xml',
        'views/dashboard.xml',
        'data/automation.xml',
        'security/ir.model.access.csv',
        'report/report_template.xml',
        'report/payment.xml',
        'report/report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
