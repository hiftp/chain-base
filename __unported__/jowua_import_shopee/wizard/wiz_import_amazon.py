# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime
import tempfile
import binascii
import codecs
from datetime import date, datetime
from odoo.exceptions import Warning, UserError
from odoo import models, fields, exceptions, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

import logging
_logger = logging.getLogger(__name__)
import io
try:
	import xlrd
	from xlrd import xldate_as_tuple
except ImportError:
	_logger.debug('Cannot `import xlrd`.')
try:
	import csv
except ImportError:
	_logger.debug('Cannot `import csv`.')
try:
	import xlwt
except ImportError:
	_logger.debug('Cannot `import xlwt`.')
try:
	import cStringIO
except ImportError:
	_logger.debug('Cannot `import cStringIO`.')
try:
	import base64
except ImportError:
	_logger.debug('Cannot `import base64`.')

class ImportAmazonSale(models.TransientModel):
	_name = "import.amazon.sale"

	# def _get_company_id(self):
	# 	return self.env['res.partner'].sudo().search([('id', '=', self.env['ir.config_parameter'].sudo().get_param('import_amazon_company'))])
	#
	# def _get_tax_id(self):
	# 	return self.env['account.tax'].sudo().search([('id', '=', self.env['ir.config_parameter'].sudo().get_param('import_amazon_tax'))])
	#
	# def _get_cost_id(self):
	# 	return self.env['product.product'].sudo().search([('id', '=', self.env['ir.config_parameter'].sudo().get_param('import_amazon_cost'))])

	company_id = fields.Many2one('res.partner', string="所屬公司")
	tax_id = fields.Many2one('account.tax', string="銷售稅")
	cost_id = fields.Many2one('product.product', string="amazon折扣費用")
	order_source = fields.Selection(string="匯入來源", selection=[('國際', '國際官網'), ('台灣', '台灣官網')])
	File_slect = fields.Binary(string="選擇檔案")

	#匯入amazon訂單
	def imoport_file(self):
		try:
			fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
			fp.write(binascii.a2b_base64(self.File_slect))
			fp.seek(0)
			values = {}
			workbook = xlrd.open_workbook(fp.name)
			worksheet = workbook.sheet_by_index(0)

			first_row = []  # The row where we stock the name of the column
			for col in range(worksheet.ncols):
				first_row.append(worksheet.cell_value(3, col))
			# transform the workbook to a list of dictionaries
			archive_lines = []
			for row in range(4, worksheet.nrows):
				elm = {}
				for col in range(worksheet.ncols):
					ctype = worksheet.cell(row, col).ctype
					if ctype == 3:
						scell = worksheet.cell_value(row, col)
						celldate = datetime(*xldate_as_tuple(scell, 0))
						elm[first_row[col]] = celldate.strftime('%Y-%m-%d')
					else:
						elm[first_row[col]] = worksheet.cell_value(row, col)
				archive_lines.append(elm)
		except:
			raise Warning(_("Invalid file!"))

		amaxon_txn_obj = self.env['import.amazon.txn']
		cont = 0
		for line in archive_lines:
			sale_no = str(line.get(u'日期', "")).strip(),
			if sale_no:
				vals = {
					'import_date': datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
					'date': str(line.get(u'日期', "")).strip(),
					'order': str(line.get(u'订单编号', "")).strip(),
					'sku': str(line.get(u'SKU', "")).strip(),
					'txn_type': str(line.get(u'交易类型', "")).strip(),
					'payment_type': str(line.get(u'付款类型', "")).strip(),
					'payment_detail': str(line.get(u'付款详情', "")).strip(),
					'amount': str(line.get(u'金额', "")).strip(),
					'quantity': str(line.get(u'数量', "")).strip(),
					'product_title': str(line.get(u'商品名称', "")).strip(),
				}
				amaxon_txn_obj.create(vals)
		return {'type': 'ir.actions.act_window_close'}

