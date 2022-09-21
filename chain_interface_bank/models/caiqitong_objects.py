# -*- coding: utf-8 -*-
import json
import logging

from pyexpat import ExpatError

from odoo import fields, models, api
from odoo.exceptions import UserError
from cqt_functions import CqtFunction as cqt


class InterfaceGuiShuBank(models.Model):
    _name = 'interface.bank'
    _description = u'归属银行管理'
    _rec_name = 'name'

    name = fields.Char(string=u'银行名称', required=True)
    code = fields.Char(string=u'银行代码', required=True)

    @api.model
    def create(self, vals):
        banks = self.env['interface.bank'].sudo().search([('code', '=', vals['code'])])
        if len(banks) >= 1:
            raise UserError(u"请不要重复创建!")
        return super(InterfaceGuiShuBank, self).create(vals)


class InterfaceOpenBank(models.Model):
    _name = 'interface.bank.deposit'
    _description = u'开户行管理'
    _rec_name = 'name'

    name = fields.Char(string=u'银行网点名称', required=True)
    code = fields.Char(string=u'网点联行号/CNAPS', required=True)
    add = fields.Char(string=u'网点地址', required=True)
    bank_id = fields.Many2one(comodel_name='interface.bank', string=u'归属银行')

    @api.model
    def create(self, vals):
        banks = self.env['interface.bank.deposit'].sudo().search([('code', '=', vals['code'])])
        if len(banks) >= 1:
            raise UserError(u"请不要重复创建!")
        return super(InterfaceOpenBank, self).create(vals)


class InterfaceBankShengFen(models.Model):
    _name = 'interface.bank.province'
    _description = u'省份管理'
    _rec_name = 'name'

    name = fields.Char(string=u'单位名称', required=True)
    code = fields.Char(string=u'行政区划代码', required=True)
    deposit_id = fields.Many2one(comodel_name='interface.bank.deposit', string=u'开户行')

    @api.model
    def create(self, vals):
        banks = self.env['interface.bank.province'].sudo().search([('code', '=', vals['code'])])
        if len(banks) >= 1:
            raise UserError(u"请不要重复创建!")
        return super(InterfaceBankShengFen, self).create(vals)


class InterfaceBankCity(models.Model):
    _name = 'interface.bank.city'
    _description = u'城市代码管理'
    _rec_name = 'name'

    name = fields.Char(string=u'单位名称', required=True)
    code = fields.Char(string=u'行政区划代码', required=True)
    province_id = fields.Many2one(comodel_name='interface.bank.province', string=u'省份')

    @api.model
    def create(self, vals):
        banks = self.env['interface.bank.city'].sudo().search([('code', '=', vals['code'])])
        if len(banks) >= 1:
            raise UserError(u"请不要重复创建!")
        return super(InterfaceBankCity, self).create(vals)


class InterfaceCurrency(models.Model):
    _name = 'bank.currency'
    _description = u'币种管理'
    _rec_name = 'name'

    name = fields.Char(string=u'币种中文名', required=True)
    code = fields.Char(string=u'币种代码', required=True)
    number = fields.Char(string=u'用于农行代码')

    @api.model
    def create(self, vals):
        banks = self.env['bank.currency'].sudo().search([('code', '=', vals['code'])])
        if len(banks) >= 1:
            raise UserError(u"请不要重复创建!")
        return super(InterfaceCurrency, self).create(vals)


class BillStorage(models.Model):
    _name = 'interface.bank.bill.storage'
    _inherit = 'mail.thread'
    _description = u"票据入库单"
    _rec_name = 'custNo'

    company_id = fields.Many2one('res.company', string=u'公司', default=lambda self: self.env.user.company_id.id)
    requestId = fields.Char(string=u'单笔唯一标识')
    batchId = fields.Char(string=u'批次号', required=True)
    custNo = fields.Char(string=u'持有人客户编号', required=True)
    custName = fields.Char(string=u'持有人客户名称', required=True)
    line_ids = fields.One2many(comodel_name='interface.bank.bill.storage.line', inverse_name='storage_id', string=u'票据')
    state = fields.Selection(string=u'状态', selection=[('0', u'未上载'), ('1', u'已上载'), ], default='0')

    @api.multi
    def upload_storage(self):
        """将单据数据上载至财企通系统"""
        for bill in self:
            logging.info(u"开始上载票据至财企通系统")
            # 获取财企通前置机地址
            service_url = self.env['ir.values'].get_default('interface.bank.settings', 'feg_add')
            # 封装xml
            str_xml = cqt.package_bill_storage_to_xml(bill)
            logging.info(str_xml)
            result_xml = cqt.send_xml_to_cqtbankservice(str_xml, service_url)
            # 解析xml
            try:
                # 解析报文
                result_json = cqt.xml_to_json(result_xml)
            except KeyError as e:
                raise UserError(u"交易发生KeyError异常！\r\n消息KeyError字段：{}".format(e.message))
            except ExpatError as e:
                raise UserError(u"财企通服务器通信故障！请检查前置机日志输出!\r\n{}".format(e.message))
            result_json = json.loads(result_json.strip())
            efmp = result_json['efmp']
            result = cqt.parsing_result_xml_result(efmp)
            if result['resultCode'] != '0000':
                msg = u"""执行失败！反馈代码: (%s),反馈消息: (%s)""" % (result['resultCode'], result['resultMsg'])
                logging.info(msg)
                raise UserError(msg)
            else:
                bill.message_post(body=result['resultMsg'], message_type='notification')
                bill.state = '1'
        return True

    @api.model
    def create(self, vals):
        if not vals['requestId']:
            vals['requestId'] = self.env['ir.sequence'].sudo().next_by_code('interface.bank.bill.storage.number')
        return super(BillStorage, self).create(vals)


class BillStorageLine(models.Model):
    _name = 'interface.bank.bill.storage.line'
    _description = u"票据入库列表（30001）"

    storage_id = fields.Many2one(comodel_name='interface.bank.bill.storage', string=u'票据入库单')
    draftNo = fields.Char(string=u'票据号', required=True)
    draftTp = fields.Selection(string=u'票据种类', selection=[('AC01', u'银行承兑汇票'), ('AC02', u'商业承兑汇票')], required=True)
    draftCls = fields.Selection(string=u'票据类型', selection=[('4', u'其他类型')], required=True)
    draftSource = fields.Selection(string=u'票据来源', selection=[('0', u'纸质')], required=True)
    isseDate = fields.Date(string=u'出票日', required=True)
    dueDate = fields.Date(string=u'到期日', required=True)
    accptrDate = fields.Date(string=u'承兑日期')
    isseAmt = fields.Char(string=u'票面金额', required=True)
    drwrAcnt = fields.Char(string=u'出票人账户')
    drwrName = fields.Char(string=u'出票人名称', required=True)
    pyeeAcnt = fields.Char(string=u'收票人账户')
    pyeeName = fields.Char(string=u'收票人名称')
    pyeeAcctsvcr = fields.Char(string=u'收票人开户行号')
    pyeeAcctsvcrName = fields.Char(string=u'收票人开户行名')
    accptrAcnt = fields.Char(string=u'承兑人/行账户')
    accptrName = fields.Char(string=u'承兑人/行名称', required=True)
    accptrBank = fields.Char(string=u'承兑人所属行号/承兑行号', required=True)
    accptrBankName = fields.Char(string=u'承兑人所属行名称/承兑行名')
    accptrAcctsvcr = fields.Char(string=u'承兑人/行开户行号')
    accptrAcctsvcrName = fields.Char(string=u'承兑人/行开户行名')
    accptrAddr = fields.Char(string=u'承兑人/行地址')
    accptrCtrctNo = fields.Char(string=u'承兑协议编号')
    txCtrctNb = fields.Char(string=u'交易合同号')
    bnkEndrsmtmk = fields.Selection(string=u'是否可以转让', selection=[('0', u'是'), ('1', u'否')])
    preHolderName = fields.Char(string=u'前手')


class WeeklyFundingPlan(models.Model):
    _name = 'bank.weekly.funding.plan'
    _inherit = 'mail.thread'
    _description = u"资金池周计划"
    _rec_name = 'custName'

    company_id = fields.Many2one('res.company', string=u'公司', default=lambda self: self.env.user.company_id.id)
    requestId = fields.Char(string=u'唯一标识')
    custNo = fields.Char(string=u'客户编号', required=True)
    custName = fields.Char(string=u'客户名称', required=True)
    startDate = fields.Date(string=u'开始日期(周一)', required=True)
    endDate = fields.Date(string=u'开始日期(周日)', required=True)
    weekUp = fields.Float(string=u'周上划资金', digits=(10, 2), required=True)
    weekDown = fields.Float(string=u'周下拨资金', digits=(10, 2), required=True)
    mondayUp = fields.Float(string=u'周一上划资金', digits=(10, 2), required=True)
    mondayDown = fields.Float(string=u'周一下拨资金', digits=(10, 2), required=True)
    tuesdayUp = fields.Float(string=u'周二上划资金', digits=(10, 2), required=True)
    tuesdayDown = fields.Float(string=u'周二下拨资金', digits=(10, 2), required=True)
    wednesdayUp = fields.Float(string=u'周三上划资金', digits=(10, 2), required=True)
    wednesdayDown = fields.Float(string=u'周三下拨资金', digits=(10, 2), required=True)
    thursdayUp = fields.Float(string=u'周四上划资金', digits=(10, 2), required=True)
    thursdayDown = fields.Float(string=u'周四下拨资金', digits=(10, 2), required=True)
    fridayUp = fields.Float(string=u'周五上划资金', digits=(10, 2), required=True)
    fridayDown = fields.Float(string=u'周五下拨资金', digits=(10, 2), required=True)
    saturdayUp = fields.Float(string=u'周六上划资金', digits=(10, 2), required=True)
    saturdayDown = fields.Float(string=u'周六下拨资金', digits=(10, 2), required=True)
    sundayUp = fields.Float(string=u'周日上划资金', digits=(10, 2), required=True)
    sundayDown = fields.Float(string=u'周日下拨资金', digits=(10, 2), required=True)
    state = fields.Selection(string=u'状态', selection=[('0', u'未上载'), ('1', u'已上载'), ], default='0')

    @api.multi
    def upload_weekly_funding_plan(self):
        logging.info(u"开始上传资金池周计划到财企通系统")
        for plan in self:
            # 获取财企通前置机地址
            service_url = self.env['ir.values'].get_default('interface.bank.settings', 'feg_add')
            # 封装xml
            str_xml = cqt.package_weekly_funding_plan_to_xml(plan)
            logging.info(str_xml)
            result_xml = cqt.send_xml_to_cqtbankservice(str_xml, service_url)
            try:
                # 解析报文
                result_json = cqt.xml_to_json(result_xml)
            except KeyError as e:
                raise UserError(u"交易发生KeyError异常！\r\n消息KeyError字段：{}".format(e.message))
            except ExpatError as e:
                raise UserError(u"财企通服务器通信故障！请检查前置机日志输出!\r\n{}".format(e.message))
            result_json = json.loads(result_json.strip())
            efmp = result_json['efmp']
            result = cqt.parsing_result_xml_result(efmp)
            if result['resultCode'] != '0000':
                msg = u"""执行失败！反馈代码: (%s),反馈消息: (%s)""" % (result['resultCode'], result['resultMsg'])
                logging.info(msg)
                raise UserError(msg)
            else:
                message = u"""结果码：(%s),返回消息：（%s）""" % (result['resultCode'], result['resultMsg'])
                plan.message_post(body=message, message_type='notification')
                plan.state = '1'
        return True

    @api.model
    def create(self, vals):
        if not vals['requestId']:
            vals['requestId'] = self.env['ir.sequence'].sudo().next_by_code('bank.weekly.funding.plan.number')
        return super(WeeklyFundingPlan, self).create(vals)
