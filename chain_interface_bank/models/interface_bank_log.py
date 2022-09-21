# -*- coding: utf-8 -*-
import datetime
from odoo import fields, models


class InterfaceBankLog(models.Model):
    _name = 'interface.bank.log'
    _description = u'银企直联日志记录'

    company_id = fields.Many2one(comodel_name='res.company', string=u'公司')
    bank_type = fields.Selection(string=u'涉及银行', selection=[('00', u'财企通'), ('01', u'农业银行'), ], default='00')
    public_account_id = fields.Many2one(comodel_name='bank.public.accounts', string=u'付款账户')
    form_code = fields.Char(string=u'单据编号')
    transaction_type = fields.Selection(string=u'交易类型', selection=[('00', u'付款'), ('01', u'查询'), ], default='00')
    partner_id = fields.Char(string=u'涉及户名')
    partner_bank_number = fields.Char(string=u'涉及账号')
    pay_money = fields.Float(string=u'产生金额')
    stated = fields.Char(string=u'说明')
    create_date = fields.Datetime(string=u'创建时间', default=datetime.datetime.now())
