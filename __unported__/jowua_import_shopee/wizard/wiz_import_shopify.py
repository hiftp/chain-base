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

class ImportshopifySale(models.TransientModel):
	_name = "import.shopify.sale"

	def _get_company_id(self):
		return self.env['res.partner'].sudo().search([('id', '=', self.env['ir.config_parameter'].sudo().get_param('import_shopify_company'))])

	def _get_tax_id(self):
		return self.env['account.tax'].sudo().search([('id', '=', self.env['ir.config_parameter'].sudo().get_param('import_shopify_tax'))])

	def _get_cost_id(self):
		return self.env['product.product'].sudo().search([('id', '=', self.env['ir.config_parameter'].sudo().get_param('import_shopify_cost'))])

	company_id = fields.Many2one('res.partner', string="所屬公司", required=True, default=_get_company_id)
	tax_id = fields.Many2one('account.tax', string="銷售稅", required=False, default=_get_tax_id)
	cost_id = fields.Many2one('product.product', string="shopify折扣費用", required=True, default=_get_cost_id)
	order_source = fields.Selection(string="匯入來源", selection=[('國際', '國際官網'), ('台灣', '台灣官網'), ], required=True)
	File_slect = fields.Binary(string="選擇檔案")

		# 匯入銷帳 國際(美金)hitrust xls
	def imoport_hitrust_us_invoice_file(self):
		fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xls")
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

		for line in archive_lines:
			if str(line.get('編號', "")).strip() == '':
				break
			csv_date = str(line.get('訂單日期', "")).strip()
			csv_price = float(str(line.get('交易金額', "")).strip())
			csv_saleno = str(line.get('訂單號碼', "")).strip()
			if csv_saleno == '':
				continue
			sale_order = self.env['sale.order'].search([('client_order_ref', 'ilike', csv_saleno)], limit=1)
			if sale_order:
				sale_order.update({
					'write_off_date': datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
					'write_off_importdate': datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
					'write_off_amount': csv_price,
					'write_off_memo': '國際(美金)hitrust',
				})

		return {'type': 'ir.actions.act_window_close'}

	#匯入銷帳 skbank csv
	def imoport_skbank_invoice_file(self):
		fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
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

		for line in archive_lines:
			if str(line.get('編號', "")).strip() == '':
				break
			csv_date = str(line.get('請退款日期', "")).strip()
			csv_price = float(str(line.get('金額', "")).strip())
			csv_saleno = str(line.get('訂單編號', "")).strip()
			if csv_saleno == '':
				continue
			sale_order = self.env['sale.order'].search([('client_order_ref', 'ilike', csv_saleno)], limit=1)
			if sale_order:
				sale_order.update({
					'write_off_date': datetime.strptime(csv_date, "%Y-%m-%d %H:%M:%S.%f"),
					'write_off_importdate': datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
					'write_off_amount': csv_price,
					'write_off_memo': '新光外幣',
				})

		return {'type': 'ir.actions.act_window_close'}

		# 匯入銷帳 台灣 Hitrust xls
	def imoport_hitrust_invoice_file(self):
		fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xls")
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

		for line in archive_lines:
			if str(line.get('編號', "")).strip() == '':
				break
			csv_date = str(line.get('請退款日期', "")).strip()
			csv_price = float(str(line.get('金額', "")).strip())
			csv_saleno = str(line.get('訂單編號', "")).strip()
			if csv_saleno == '':
				continue
			sale_order = self.env['sale.order'].search([('client_order_ref', 'ilike', csv_saleno)], limit=1)
			if sale_order:
				sale_order.update({
					'write_off_date': datetime.strptime(csv_date, "%Y-%m-%d %H:%M:%S.%f"),
					'write_off_importdate': datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
					'write_off_amount': csv_price,
					'write_off_memo': '台灣 Hitrus',
				})

		return {'type': 'ir.actions.act_window_close'}

	#匯入銷帳 paypal csv
	def imoport_paypal_invoice_file(self):
		file_path = tempfile.gettempdir() + '/file.csv'
		data = self.File_slect
		f = open(file_path, 'wb')
		f.write(base64.b64decode(data))
		f.close()
		archive = csv.DictReader(open(file_path, encoding="utf_8", errors='ignore'))
		archive_lines = []
		for line in archive:
			archive_lines.append(line)

		for line in archive_lines:
			# csv_date = str(line.get('\ufeff"日期"', "")).strip()
			# csv_time = str(line.get('時間', "")).strip()
			# csv_price = self.get_valid_price(str(line.get('總額', "0")).strip())
			# csv_saleno = '國際'+str(line.get('帳單號碼', "")).strip()
			# csv_paytkind = str(line.get('類型', "")).strip()
			csv_date = str(line.get('\ufeff"Date"', "")).strip()
			csv_time = str(line.get('Time', "")).strip()
			csv_price = self.get_valid_price(str(line.get('Gross', "0")).strip())
			csv_saleno = str(line.get('Invoice Number', "")).strip()
			csv_paytkind = str(line.get('Type', "")).strip()
			if csv_saleno == '':
				continue
			sale_order = self.env['sale.order'].search([('client_order_ref', 'ilike', csv_saleno)], limit=1)
			if sale_order:
				if csv_price < 0:
					sale_order.update({
						# 'write_off_date': datetime.strptime(csv_date, "%Y/%m/%d"),
						'write_off_refund_date': datetime.strptime(csv_date, "%Y/%m/%d"),
						'write_off_importdate': datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
						# 'write_off_amount': ,
						'write_off_refund': csv_price,
						'write_off_memo': csv_date+' '+csv_time+'-paypal-'+csv_paytkind,
					})
				else:
					sale_order.update({
						'write_off_date': datetime.strptime(csv_date, "%Y/%m/%d"),
						'write_off_importdate': datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
						'write_off_amount': csv_price,
						'write_off_memo': csv_date+' '+csv_time+'-paypal-'+csv_paytkind,
					})

		return {'type': 'ir.actions.act_window_close'}

	#匯入shopify訂單
	def imoport_file(self):
		self.env['ir.config_parameter'].sudo().set_param('import_shopify_company', self.company_id.id)
		self.env['ir.config_parameter'].sudo().set_param('import_shopify_tax', self.tax_id.id)
		self.env['ir.config_parameter'].sudo().set_param('import_shopify_cost', self.cost_id.id)
		file_path = tempfile.gettempdir() + '/file.csv'
		data = self.File_slect
		f = open(file_path, 'wb')
		f.write(base64.b64decode(data))
		f.close()
		archive = csv.DictReader(open(file_path, encoding="utf_8", errors='ignore'))
		archive_lines = []
		for line in archive:
			archive_lines.append(line)

		product_obj = self.env['product.product']
		product_template_obj = self.env['product.template']
		sale_order_line_obj = self.env['sale.order.line']

		self.valid_columns_keys(archive_lines)

		cont = 0
		for line in archive_lines:
			cont += 1
			partner_id = self.find_partner(line) # 尋找客戶編號
			sale_no1 = str(line.get('Name', "")).strip()
			sale_no2 = str(line.get('Payment Reference', "")).strip()
			sale_no = self.order_source+sale_no1+','+sale_no2
			sale_order_id, sale_cost = self.find_saleorder(sale_no, partner_id, line)
			if not sale_order_id:
				continue

			code = str(line.get('Lineitem sku', "")).strip()
			product_id = product_obj.search([('default_code', '=', code)])
			quantity = float(line.get('Lineitem quantity', 0))
			price = self.get_valid_price(line.get('Lineitem price', ""))
			price_unit = round(((quantity * price)-sale_cost) / quantity,2)
			product_uom = product_template_obj.search([('default_code', '=', code)])

			if sale_order_id and product_id:
				vals = {
					'order_id': sale_order_id.id,
					'product_id': product_id.id,
					'product_uom_qty': float(quantity),
					'price_unit': price_unit,
					'product_uom': product_id.product_tmpl_id.uom_po_id.id,
					'name': product_id.name,
					'tax_id': self.tax_id,
					#'tax_id': [(6, 0, self.tax_id)],
				}
				sale_order_line_obj.create(vals)
		return {'type': 'ir.actions.act_window_close'}

	#尋找客戶，若無則建立
	def find_partner(self, importline):
		sale_no = str(importline.get('Name', "")).strip()
		user_email = str(importline.get('Email', "")).strip()
		user_name = str(importline.get('Shipping Name', "")).strip()
		user_street = str(importline.get('Shipping Street', "")).strip()
		user_addr1 = str(importline.get('Shipping Address1', "")).strip()
		user_addr2 = str(importline.get('Shipping Address2', "")).strip()
		user_city = str(importline.get('Shipping City', "")).strip()
		user_zip = str(importline.get('Shipping Zip', "")).strip()
		user_country = str(importline.get('Shipping Country', "")).strip()
		user_phone = str(importline.get('Shipping Phone', "")).strip()
		user_mobile = str(importline.get('Phone', "")).strip()
		user_state = str(importline.get('Shipping Province', "")).strip()
		user_state_name = str(importline.get('Shipping Province Name', "")).strip()

		res_partner = self.env['res.partner']
		partner_search = res_partner.search([('name', '=', self.order_source+sale_no+' '+user_name)], limit=1)
		country_search = self.env['res.country'].search([('code', '=', user_country)])
		country_state_search = self.env['res.country.state'].search([('code', '=', user_state), ('country_id', '=', country_search.id)])

		if partner_search:
			return partner_search
		else:
			partner_id = res_partner.create({
				'company_type': 'person',
				'type': 'delivery',
				'parent_id': self.company_id.id,
				'name': self.order_source+sale_no+' '+user_name,
				'street': user_street,
				'street2': user_addr1+' '+user_addr2,
				'phone': user_phone,
				'mobile': user_mobile,
				'country_id': country_search.id,
				'state_id': country_state_search.id,
				'city': user_city,
				'zip': user_zip,
				'email': user_email,
				})
			return partner_id

	#尋找訂單，若無則建立
	def find_saleorder(self, saleno, partner_id, importline):
		sale_order = self.env['sale.order']
		sale_order_line_obj = self.env['sale.order.line']
		sale_search = sale_order.search([('client_order_ref', 'ilike', saleno)])

		if sale_search:
			return sale_search, 0
		else:
			if str(importline.get('Financial Status', "")).strip() != 'paid':
				return False, 0
			#尋找價格表 USD
			sale_currency = str(importline.get('Currency', "").strip())
			currency_search = self.env['res.currency'].search([('name', '=', sale_currency)])
			pricelist_search = self.env['product.pricelist'].search([('currency_id', '=', currency_search.id)], limit=1)
			csv_total = float(importline.get('Total', "").strip())
			sale_id = sale_order.create({
				'partner_id': partner_id.id,
				'client_order_ref': saleno,
				'pricelist_id': pricelist_search.id,
				'write_off_amount': csv_total,
				})
			print(importline.get('Shipping', "0"))
			sale_cost1 = float(str(importline.get('Shipping', "0")).strip())
			if sale_cost1 != 0:
				vals = {
					'order_id': sale_id.id,
					'product_id': self.cost_id.id,
					'product_uom_qty': 1,
					'price_unit': sale_cost1,
					'product_uom': self.cost_id.product_tmpl_id.uom_po_id.id,
					'name': self.cost_id.name
				}
				sale_order_line_obj.create(vals)

			sale_cost = float(str(importline.get('Discount Amount', "0")).strip())
			return sale_id, sale_cost

	#尋找shopify客戶訂單，若無則建立
	def find_shopify_user(self, saleno):
		sale_order = self.env['sale.order']
		sale_search = sale_order.search([('client_order_ref', '=', saleno)])

		if sale_search:
			return sale_search
		else:
			sale_id = sale_order.create({
				'partner_id': self.env.user.partner_id.id,
				'client_order_ref': saleno,
				})
			return sale_id



	def valid_columns_keys(self, archive_lines):
		columns = archive_lines[0].keys()
		print
		"columns>>", columns
		text = "匯入必需包含下列欄位:";
		text2 = text
		if not 'Name' in columns:
			text += "\n[ 訂單編號 ]"
		if not 'Shipping Name' in columns:
			text += "\n[ 買家帳號 ]"
		if not 'Payment Reference' in columns:
			text += "\n[ 銷帳編號 ]"
		if text != text2:
			raise UserError(text)
		return True

	def get_valid_price(self, price):
		if price != "":
			price = str(price).replace("$", "").replace(",", "")
		try:
			price_float = float(price)
			return price_float
		except:
			raise UserError(
				"總額 %s 無法轉成數字" % price)
		return False


# 	def create_chart_accounts(self,values):
#
# 		if values.get("code") == "":
# 			raise Warning(_('Code field cannot be empty.') )
#
# 		if values.get("name") == "":
# 			raise Warning(_('Name field cannot be empty.') )
#
# 		if values.get("user") == "":
# 			raise Warning(_('type field cannot be empty.'))
#
# 		if values.get("code"):
# 			s = str(values.get("code"))
# 			code_no = s.rstrip('0').rstrip('.') if '.' in s else s
#
# 		account_obj = self.env['account.account']
# 		account_search = account_obj.search([
# 			('code', '=', values.get('code'))
# 			])
#
# 		is_reconcile = False
# 		is_deprecated= False
#
# 		if values.get("reconcile") == 'TRUE' or values.get("reconcile") == "1":
# 			is_reconcile = True
#
# 		if values.get("deprecat") == 'TRUE'  or values.get("deprecat") == "1":
# 			is_deprecated = True
#
# 		user_id = self.find_user_type(values.get('user'))
# 		currency_get = self.find_currency(values.get('currency'))
# 		# tag_ids = self.find_tags(values.get('tag'))
# 		group_get = self.find_group(values.get('group'))
#
# # --------tax-
# 		tax_ids = []
# 		if values.get('tax'):
# 			if ';' in  values.get('tax'):
# 				tax_names = values.get('tax').split(';')
# 				for name in tax_names:
# 					tax= self.env['account.tax'].search([('name', '=', name)])
# 					if not tax:
# 						raise Warning(_('%s Tax not in your system') % name)
# 					for t in tax:
# 						tax_ids.append(t)
#
# 			elif ',' in  values.get('tax'):
# 				tax_names = values.get('tax').split(',')
# 				for name in tax_names:
# 					tax= self.env['account.tax'].search([('name', '=', name)])
# 					if not tax:
# 						raise Warning(_('%s Tax not in your system') % name)
# 					for t in tax:
# 						tax_ids.append(t)
# 			else:
# 				tax_names = values.get('tax').split(',')
# 				tax= self.env['account.tax'].search([('name', '=', tax_names)])
# 				if not tax:
# 					raise Warning(_('"%s" Tax not in your system') % tax_names)
# 				for t in tax:
# 					tax_ids.append(t)
#
# # ------------tags
# 		tag_ids = []
# 		if values.get('tag'):
# 			if ';' in  values.get('tag'):
# 				tag_names = values.get('tag').split(';')
# 				for name in tag_names:
# 					tag= self.env['account.account.tag'].search([('name', '=', name)])
# 					if not tag:
# 						raise Warning(_('"%s" Tag not in your system') % name)
# 					tag_ids.append(tag)
#
# 			elif ',' in  values.get('tag'):
# 				tag_names = values.get('tag').split(',')
# 				for name in tag_names:
# 					tag= self.env['account.account.tag'].search([('name', '=', name)])
# 					if not tag:
# 						raise Warning(_('"%s" Tag not in your system') % name)
# 					tag_ids.append(tag)
# 			else:
# 				tag_names = values.get('tag').split(',')
# 				tag= self.env['account.account.tag'].search([('name', '=', tag_names)])
# 				if not tag:
# 					raise Warning(_('"%s" Tag not in your system') % tag_names)
# 				tag_ids.append(tag)
#
# 		data={
# 				'code' : code_no,
# 				'name' : values.get('name'),
# 				'user_type_id':user_id.id,
# 				'tax_ids':[(6,0,[y.id for y in tax_ids])]if values.get('tax') else False,
# 				'tag_ids':[(6,0,[x.id for x in tag_ids])]if values.get('tag') else False,
# 				'group_id':group_get.id,
# 				'currency_id':currency_get or False,
# 				'reconcile':is_reconcile,
# 				'deprecated':is_deprecated,
#
# 				}
# 		chart_id = account_obj.create(data)
#
# 		return chart_id
#
# # ---------------------------user-----------------
#
#
# 	def find_user_type(self,user):
# 		user_type=self.env['account.account.type']
# 		user_search = user_type.search([('name','=',user)])
# 		if user_search:
# 			return user_search
# 		else:
# 			raise Warning(_('Field User is not correctly set.'))
#
# # --------------------currency------------------
#
#
# 	def find_currency(self, name):
# 		currency_obj = self.env['res.currency']
# 		currency_search = currency_obj.search([('name', '=', name)])
# 		if currency_search:
# 			return currency_search.id
# 		else:
# 			if name == "":
# 				pass
# 			else:
# 				raise Warning(_(' %s currency are not available.') % name)
#
# # -----------------group-------
#
#
# 	def find_group(self,group):
# 		group_type=self.env['account.group']
# 		group_search = group_type.search([('name','=',group)])
#
# 		if group_search:
# 			return group_search
# 		else:
# 			group_id = group_type.create({
# 				'name' : group
# 				})
# 			return group_id
