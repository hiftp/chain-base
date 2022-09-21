# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError


class BankPublicAccounts(models.Model):
    _name = 'bank.public.accounts'
    _rec_name = 'costomer_name'
    _description = u'银企直联内部账户'

    company_id = fields.Many2one(comodel_name='res.company', string=u'公司', required=True)
    costomer_name = fields.Char(string=u'客户名称')
    costomer_number = fields.Char(string=u'客户编号')
    payment_number = fields.Char(string=u'账号', required=True)
    payment_username = fields.Char(string=u'户名')
    payment_bank = fields.Many2one(comodel_name='interface.bank', string=u'归属银行')
    deposit_id = fields.Many2one(comodel_name='interface.bank.deposit', string=u'开户行')
    dprovince_id = fields.Many2one(comodel_name='interface.bank.province', string=u'省份')
    city_id = fields.Many2one(comodel_name='interface.bank.city', string=u'城市')
    btype = fields.Selection(string=u'用于范围', selection=[('00', u'财企通'), ('01', u'农业银行'), ('02', u'皆可')], required=True, default='00')

    @api.model
    def create(self, vals):
        accounts = self.env['bank.public.accounts'].sudo().search([('payment_number', '=', vals['payment_number'])])
        if len(accounts) >= 1:
            raise UserError(u"请不要重复创建!")
        return super(BankPublicAccounts, self).create(vals)


class BankExternalAccounts(models.Model):
    _name = 'bank.external.accounts'
    _rec_name = 'name'
    _description = u'银企直联外部账户'

    name = fields.Char(string=u'名称')
    e_bank_number = fields.Char(string=u'外部银行卡号', required=True)
    e_bank_name = fields.Char(string=u'外部银行户名', required=True)
    account_id = fields.Many2one(comodel_name='bank.public.accounts', string=u'关联内部账户', required=True)
    payment_bank = fields.Many2one(comodel_name='interface.bank', string=u'归属银行')
    deposit_id = fields.Many2one(comodel_name='interface.bank.deposit', string=u'开户行', required=True)
    dprovince_id = fields.Many2one(comodel_name='interface.bank.province', string=u'省份')
    city_id = fields.Many2one(comodel_name='interface.bank.city', string=u'城市')
    company_id = fields.Many2one('res.company', string=u'公司', default=lambda self: self.env.user.company_id.id)

    @api.constrains('e_bank_name', 'deposit_id')
    def constrains_name(self):
        for res in self:
            if res.e_bank_name and res.deposit_id:
                name_str = """%s/%s""" % (res.e_bank_name,res.deposit_id.name)
                res.write({'name': name_str})
