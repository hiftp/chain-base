# -*- coding: utf-8 -*-
from decimal import Decimal

from odoo import models, fields, api
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class PaymentLine(models.Model):
    _name = 'interface.bank.payment.line'
    _description = u"付款支付记录"

    payment_id = fields.Many2one('interface.bank.payment', string=u"待支付")
    pay_per_money = fields.Float(string=u"支付金额")
    state = fields.Selection(
        [('unpaied', u'已提交'),
         ('done', u'已过审'), ('undone', u'未过审'),
         ('paied', u'已支付')],
        string=u'提交状态', default=u'unpaied')
    pay_per_money_char = fields.Char(string=u"支付金额", compute='float2char', store=True)

    @api.depends('pay_per_money')
    def float2char(self):
        for line in self:
            line.pay_per_money_char = str(Decimal(line.pay_per_money).quantize(Decimal('0.00')))
