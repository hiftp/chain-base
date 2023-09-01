# -*- coding: utf-8 -*-
{
    'name': 'IoTPay Payment Acquirer',
    'category': 'Accounting/Payment Acquirers',
    'version': '2.0',
    "author": "odooChain",
    "maintainer": "odooChain",
    'sequence': 350,
    'summary': 'Payment Acquirer: IoTPay Implementation',
    'description': """IoTPay Payment Acquirer""",
    'depends': ['account_payment', 'payment'],
    'data': [
        'views/payment_views.xml',
        'data/payment_acquirer_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_iotpay/static/src/js/**/*',
        ],
    },
    'application': True,
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
