# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    write_off_memo = fields.Char(string="銷帳說明", required=False, )
    write_off_amount = fields.Float(string="銷帳金額",  required=False, )
    write_off_refund = fields.Float(string="退款金額", required=False, )
    write_off_refund_date = fields.Date(string="退款日期", required=False, )
    write_off_date = fields.Date(string="銷帳日期", required=False, )
    write_off_importdate = fields.Date(string="轉入銷帳日期", required=False, )



