# -*- coding: utf-8 -*-
{
    'name': "chain_product_expiry_package",

    'summary': """
        This module add a field to save the Product Expiry Date of packages in Stock production lot
        """,

    'description': """
        This module add a field to save the Product Expiry Date of packages in Stock production lot
    """,
    'license': 'OPL-1',
    'author': "Go2Future, OdooChain",
    'website': "https://github.com/odoochain/chain-base",
    'contributors': ["Rafael Andara D <randarad@gmail.com>"],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Product',
    'version': '15.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base',  'stock', 'product_expiry'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
