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

class ImportShipSale(models.TransientModel):
	_name = "import.ship.sale"

	File_slect = fields.Binary(string="選擇檔案")

	#匯入 物流編號
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
				first_row.append(worksheet.cell_value(0, col))
			# transform the workbook to a list of dictionaries
			archive_lines = []
			for row in range(1, worksheet.nrows):
				elm = {}
				for col in range(worksheet.ncols):
					elm[first_row[col]] = worksheet.cell_value(row, col)
				archive_lines.append(elm)
		except:
			raise Warning(_("Invalid file!"))

		for line in archive_lines:
			csv_saleno = str(line.get('廠商訂單編號', "")).strip()
			if csv_saleno == '':
				continue
			csv_ship_code = str(line.get('物流碼', "")).strip()
			csv_ship_date = str(line.get('預計出貨日期', "")).strip()
			csv_ship_name = str(line.get('物流商', "")).strip()
			sale_order = None
			if 'S' in csv_saleno and len(csv_saleno) == 6:
				sale_order = self.env['sale.order'].search([('name', '=', csv_saleno)], limit=1)
			elif '#' in csv_saleno:
				saleno = '國際'+csv_saleno
				sale_order = self.env['sale.order'].search([('client_order_ref', 'ilike', saleno)], limit=1)
			elif len(csv_saleno) == 4:
				saleno = '台灣#' + csv_saleno
				sale_order = self.env['sale.order'].search([('client_order_ref', 'ilike', saleno)], limit=1)
			elif len(csv_saleno) > 6:
				saleno = csv_saleno
				sale_order = self.env['sale.order'].search([('client_order_ref', 'ilike', saleno)], limit=1)

			if sale_order:
				sale_order.update({
					'ship_code': csv_ship_code,
					'ship_date': csv_ship_date,
					'ship_name': csv_ship_name,
				})

		return {'type': 'ir.actions.act_window_close'}

