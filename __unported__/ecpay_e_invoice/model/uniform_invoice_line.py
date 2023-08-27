#-*- coding:utf-8 -*-
from odoo import _, models, fields, api
from odoo.exceptions import UserError


class UniformInvoiceLine(models.Model):
    _name = 'uniform.invoice.line'
    _description = '電子發票明細'

    invoice_id = fields.Many2one(comodel_name='uniform.invoice', string='電子發票')
    name = fields.Char(string='商品名稱', required=True)
    product_id = fields.Many2one(comodel_name='product.product', string='商品')
    quantity = fields.Float(string='數量', digits=(6, 2), default=1)
    price = fields.Float(string='單價', digits=(8, 4))
    total = fields.Float(string='小計', digits=(12, 4), compute='_calculate_total', store=True)

    @api.onchange('product_id')
    def _sync_to_name(self):
        product = self.product_id
        if product:
            self.name = product.name
            self.price = product.lst_price
            self._calculate_total()

    @api.depends('price', 'quantity')
    def _calculate_total(self):
        self.total = self.price * self.quantity
