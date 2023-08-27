# -*- coding: utf-8 -*-
{
	'name': 'Import Shopee of SaleOrder from CSV or Excel File',
	'summary': '匯入蝦皮excel',
	'author': 'kulius',
	'category': 'Sale',
	'version': '13.0.0.1',
	'depends': ['base', 'sale', 'sale_stock'],
	'data': [
		'security/ir.model.access.csv',
		'wizard/view_import_shopee.xml',
		'wizard/view_import_shopify.xml',
		'wizard/view_import_amazon.xml',
		'data/import_shopee_data.xml',
		'data/import_shopify_data.xml',
		"views/inherit_sale_order_views.xml",
		"views/import_amazon_txn.xml",
		"wizard/view_import_ship.xml",
		],

	'installable': True,
    'application': True,
	"license": "AGPL-3",
}

