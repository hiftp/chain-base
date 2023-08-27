# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class ImportAmazonTxn(models.Model):
    _name = 'import.amazon.txn'
    _rec_name = 'order'
    _description = '呈現 amazon 交易歷史記錄'

    import_date = fields.Date(string='匯入日期')
    date = fields.Date(string='日期')
    order = fields.Char(string='amazon訂單')
    sku = fields.Char(string='SKU')
    txn_type = fields.Char(string='交易類型')
    payment_type = fields.Char(string='付款類型')
    payment_detail = fields.Char(string='付款詳情')
    amount = fields.Float(string='金額')
    quantity = fields.Float(string='數量')
    product_title = fields.Char(string='商品名稱')





