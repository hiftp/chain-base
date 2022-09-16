# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime
import tempfile
import binascii
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

class ImportShopeeSale(models.TransientModel):
	_name = "import.shopee.sale"

	def _get_company_id(self):
		return self.env['res.partner'].sudo().search([('id', '=', self.env['ir.config_parameter'].sudo().get_param('import_shopee_company'))])

	def _get_tax_id(self):
		return self.env['account.tax'].sudo().search([('id', '=', self.env['ir.config_parameter'].sudo().get_param('import_shopee_tax'))])

	def _get_cost_id(self):
		return self.env['product.product'].sudo().search([('id', '=', self.env['ir.config_parameter'].sudo().get_param('import_shopee_cost'))])

	company_id = fields.Many2one('res.partner', string="所屬公司", required=True, default=_get_company_id)
	tax_id = fields.Many2one('account.tax', string="銷售稅", required=False, default=_get_tax_id)
	cost_id = fields.Many2one('product.product', string="折扣費用", required=True, default=_get_cost_id)
	File_slect = fields.Binary(string="選擇檔案")
	import_option = fields.Selection([('xls', 'XLS File')],string='檔案格式',default='xls')

	#匯入銷帳csv
	def imoport_invoice_file(self):
		file_path = tempfile.gettempdir() + '/file.csv'
		data = self.File_slect
		f = open(file_path, 'wb')
		f.write(base64.b64decode(data))
		f.close()
		#archive = csv.DictReader(open(file_path))
		archive = csv.reader(open(file_path, encoding="utf-8"))
		archive_lines = []
		beginwrite = False
		#配合蝦皮銷帳匯入格式
		for line in archive:
			if beginwrite:
				archive_lines.append(line)

			if str(line[0]).strip() == '日期:':
				beginwrite = True

		sale_order = self.env['sale.order']
		for line in archive_lines:
			csv_date = str(line[0]).strip()
			csv_price = str(line[2]).strip()
			csv_saleno = str(line[3]).strip()
			if csv_saleno == '':
				continue
			saleno=csv_saleno[1:15]
			sale_order = self.env['sale.order'].search([('client_order_ref', '=', saleno), ('state', '=', 'sale')], limit=1)
			if sale_order:
				sale_order.update({
					'write_off_date': datetime.strptime(csv_date, "%Y/%m/%d %H:%M"),
					'write_off_importdate': datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
					'write_off_amount': csv_price,
					'write_off_memo': '蝦皮',
				})
				# if not sale_order.invoice_ids:
				# 	sale_order._create_invoices()
				#
				# 	if sale_order.invoice_ids:
				# 		for invoice in sale_order.invoice_ids:
				# 			invoice.update({
				# 				'invoice_date': sale_order.date_order,
				# 			})
				# 			invoice.action_post()
		return {'type': 'ir.actions.act_window_close'}

	#匯入蝦皮訂單
	def imoport_file(self):

		try:
			self.env['ir.config_parameter'].sudo().set_param('import_shopee_company', self.company_id.id)
			self.env['ir.config_parameter'].sudo().set_param('import_shopee_tax', self.tax_id.id)
			self.env['ir.config_parameter'].sudo().set_param('import_shopee_cost', self.cost_id.id)

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

		product_obj = self.env['product.product']
		product_template_obj = self.env['product.template']
		sale_order_line_obj = self.env['sale.order.line']

		self.valid_columns_keys(archive_lines)
		self.valid_product_code(archive_lines, product_obj)

		cont = 0
		for line in archive_lines:
			cont += 1
			partner_id = self.find_partner(line) # 尋找客戶編號
			sale_no = str(line.get(u'訂單編號', "")).strip()
			sale_order_id, sale_cost = self.find_saleorder(sale_no, partner_id, line)

			code = str(line.get(u'商品選項貨號', "")).strip()
			product_id = product_obj.search([('default_code', '=', code)])
			quantity = line.get(u'數量', 0)
			price_unit = self.get_valid_price(line.get(u'商品原價 (品)', ""), cont)
			product_uom = product_template_obj.search([('default_code', '=', code)])
			taxes = product_id.taxes_id.filtered(
				lambda r: not product_id.company_id or r.company_id == product_id.company_id)
			tax_ids = taxes.ids
			if sale_order_id and product_id:
				vals = {
					'order_id': sale_order_id.id,
					'product_id': product_id.id,
					'product_uom_qty': float(quantity),
					'price_unit': price_unit-sale_cost,
					'product_uom': product_id.product_tmpl_id.uom_po_id.id,
					'name': product_id.name,
					'tax_id': self.tax_id,
					#'tax_id': [(6, 0, self.tax_id)],
				}
				sale_order_line_obj.create(vals)
		return {'type': 'ir.actions.act_window_close'}

	#尋找客戶，若無則建立
	def find_partner(self, importline):
		sale_no = str(importline.get(u'訂單編號', "")).strip()
		user_no = str(importline.get(u'買家帳號 (單)', "")).strip()
		user_name = str(importline.get(u'收件者姓名 (單)', "")).strip()
		user_addr = str(importline.get(u'收件地址 (單)', "")).strip()
		user_phone = str(importline.get(u'收件者電話 (單)', "")).strip()
		user_mobile = str(importline.get(u'收件者電話 (單)', "")).strip()

		res_partner = self.env['res.partner']
		partner_search = res_partner.search([('name', '=', sale_no+' '+user_name+' '+user_no)])

		if partner_search:
			return partner_search
		else:
			partner_id = res_partner.create({
				'company_type': 'person',
				'type': 'delivery',
				'parent_id': self.company_id.id,
				'name': sale_no+' '+user_name+' '+user_no,
				'street': user_addr,
				'phone': user_phone,
				'mobile': user_mobile,
				'email': '****@gmail.com',
				})
			return partner_id

	#尋找訂單，若無則建立
	def find_saleorder(self, saleno, partner_id, importline):
		sale_order = self.env['sale.order']
		sale_order_line_obj = self.env['sale.order.line']
		sale_search = sale_order.search([('client_order_ref', '=', saleno)])

		if sale_search:
			return sale_search, 0
		else:
			sale_id = sale_order.create({
				'partner_id': partner_id.id,
				#'user_id': self.env.user.partner_id.id,
				'client_order_ref': saleno,
				})

			sale_cost1 = float(str(importline.get(u'金流服務費', "")).strip())
			sale_cost2 = float(str(importline.get(u'成交手續費 (單)', "")).strip())
			sale_cost3 = float(str(importline.get(u'蝦皮信用卡活動折抵 (單)', "")).strip())
			if sale_cost1+sale_cost2+sale_cost3 != 0:
				vals = {
					'order_id': sale_id.id,
					'product_id': self.cost_id.id,
					'product_uom_qty': 1,
					'price_unit': -1 * (sale_cost1+sale_cost2+sale_cost3),
					'product_uom': self.cost_id.product_tmpl_id.uom_po_id.id,
					'name': self.cost_id.name
				}
				sale_order_line_obj.create(vals)

			sale_cost = float(str(importline.get(u'賣家折扣券折抵金額 (單)', "")).strip())
			return sale_id, sale_cost

	#尋找蝦皮客戶訂單，若無則建立
	def find_shopee_user(self, saleno):
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
		if not '訂單編號' in columns:
			text += "\n[ 訂單編號 ]"
		if not u'買家帳號 (單)' in columns:
			text += "\n[ 買家帳號 ]"
		if not '商品選項貨號' in columns:
			text += "\n[ 商品選項貨號 ]"
		if text != text2:
			raise UserError(text)
		return True


	def valid_product_code(self, archive_lines, product_obj):
		cont = 0
		for line in archive_lines:
			cont += 1
			code = str(line.get('商品選項貨號', "")).strip()
			product_id = product_obj.search([('default_code', '=', code)])
			if len(product_id) > 1:
				raise UserError("The product code of line %s is duplicated in the system." % cont)
			if not product_id:
				raise UserError("The product code of line %s can't be found in the system." % cont)

	def get_valid_price(self, price, cont):
		if price != "":
			price = str(price).replace("$", "").replace(",", ".")
		try:
			price_float = float(price)
			return price_float
		except:
			raise UserError(
				"The price of the line item %s does not have an appropriate format, for example: '100.00' - '100" % cont)
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
