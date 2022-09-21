# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError


class InterfaceAbcChargeType(models.Model):
    _name = 'interface.abc.charge.type'
    _description = u'收费种类代码'
    _rec_name = 'name'

    code = fields.Char(string=u'种类代码', required=True)
    name = fields.Char(string=u'种类名称', required=True)

    @api.model
    def create(self, vals):
        banks = self.env['interface.abc.charge.type'].sudo().search([('code', '=', vals['code'])])
        if len(banks) >= 1:
            raise UserError(u"请不要重复创建!")
        return super(InterfaceAbcChargeType, self).create(vals)


class InterfaceAbcProvinceCity(models.Model):
    _name = 'interface.abc.province.city'
    _description = u'农行省市代码表'
    _rec_name = 'name'

    code = fields.Char(string=u'省市代码', required=True)
    name = fields.Char(string=u'省市名称', required=True)

    @api.model
    def create(self, vals):
        banks = self.env['interface.abc.province.city'].sudo().search([('code', '=', vals['code'])])
        if len(banks) >= 1:
            raise UserError(u"请不要重复创建!代码:{}".format(vals['code']))
        return super(InterfaceAbcProvinceCity, self).create(vals)


class BankPublicAccounts(models.Model):
    _inherit = 'bank.public.accounts'
    _description = u'内部付款账户'

    dprovince_id = fields.Many2one(comodel_name='interface.bank.province', string=u'省份(财企通)')
    abc_pc = fields.Many2one(comodel_name='interface.abc.province.city', string=u'省市(农行)')


class AccountMovePayment(models.Model):
    _name = 'interface.payment.account'
    _description = u"付款科目配置"
    _rec_name = 'account_id'

    company_id = fields.Many2one(comodel_name='res.company', string=u'公司', required=True, default=lambda self: self.env.user.company_id.id)
    account_id = fields.Many2one(comodel_name='account.account', string=u'付款科目', required=True)
    account_code = fields.Char(string=u'科目代码')
    bank_type = fields.Selection(string=u'付款银行', selection=[('00', u'财企通'), ('01', u'农业银行'), ], default='00',
                                 required=True)

    @api.constrains('account_id')
    def constrains_account_code(self):
        if self.account_id:
            self.account_code = self.account_id.code

    @api.constrains('company_id', 'account_code', 'bank_type')
    def constrains_payment_account(self):
        if self.company_id and self.account_code and self.bank_type:
            res = self.search([('company_id', '=', self.company_id.id), ('account_code', '=', self.account_code),
                               ('bank_type', '=', self.bank_type)])
            if len(res) > 1:
                raise UserError(u"不能添加重复记录！")
