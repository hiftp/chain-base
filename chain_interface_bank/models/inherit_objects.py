# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


# class InheritResPartner(models.Model):
#     """拓展partner联系人表单，用于银企直联付款信息"""
#     _inherit = 'res.partner'
#
#     ibank_id = fields.Many2one(comodel_name='interface.bank', string=u'账户银行')
#     ideposit_id = fields.Many2one(comodel_name='interface.bank.deposit', string=u'开户行')
#     iprovince_id = fields.Many2one(comodel_name='interface.bank.province', string=u'省份')
#     icity_id = fields.Many2one(comodel_name='interface.bank.city', string=u'城市')
#     iback_number = fields.Char(string=u'银行账户账号')
#     iback_username = fields.Char(string=u'银行账户户名')



