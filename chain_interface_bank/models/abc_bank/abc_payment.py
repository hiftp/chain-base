# -*- coding: utf-8 -*-
import datetime
import io
import json
from pyexpat import ExpatError
from xml.etree.ElementTree import tostring
from abc_functions import ABCFunctions as abc_function
import xmltodict
from odoo import fields, models, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


# 农业银行付款确认向导
class ABCPaymentCommit(models.TransientModel):
    _name = 'interface.abc.payment.commit'
    _description = u"农业银行付款确认向导"

    FUNCTION_TYPE = [
        ('a1', u'集团内汇兑-单笔'),
        ('a2', u'汇兑-单笔对公'),
        ('a3', u'汇兑-单笔对私'),
    ]
    partner_id = fields.Char(string=u'收款户名:')
    partner_bank_number = fields.Char(string=u'收款账号:')
    pay_money = fields.Float(string=u'付款金额:', digits=(23, 2))
    CrProv = fields.Many2one(comodel_name='interface.abc.province.city', string=u'收款省市', required=True)
    partner_contact = fields.Char(string=u'收款联系人')
    partner_contact_phone = fields.Char(string=u'联系人电话')
    partner_contact_add = fields.Char(string=u'联系人地址')
    bank_type = fields.Selection(string=u'付款银行', selection=[('01', u'农业银行'), ], default='01')
    public_account_id = fields.Many2one(comodel_name='bank.public.accounts', string=u'付款账户', required=True)
    DbProv = fields.Many2one(comodel_name='interface.abc.province.city', string=u'付款省市', required=True)
    payment_type = fields.Selection(string=u'功能类型', selection=FUNCTION_TYPE, required=True, default='a3')
    conFlag = fields.Boolean(string=u'校验收款户名?')
    is_BookingFlag = fields.Selection(string=u'是否预约', selection=[('0', u'不预约'), ('1', u'预约'), ], default='0')
    BookingTime = fields.Datetime(string=u'预约时间')

    @api.model
    def default_get(self, fields):
        """获取默认值"""
        res = super(ABCPaymentCommit, self).default_get(fields)
        payment_id = self.env.context.get('active_id', False)
        payment = self.env['interface.bank.payment'].browse(payment_id)
        if payment:
            if 'partner_id' in fields:
                res.update({'partner_id': payment.partner_id})
            if 'partner_bank_number' in fields:
                res.update({'partner_bank_number': payment.partner_bank_number})
            if 'pay_money' in fields:
                res.update({'pay_money': payment.pay_money})
            if 'partner_contact' in fields:
                res.update({'partner_contact': payment.partner_contact})
            if 'partner_contact_phone' in fields:
                res.update({'partner_contact_phone': payment.partner_contact_phone})
            if 'partner_contact_add' in fields:
                res.update({'partner_contact_add': payment.partner_contact_add})
            return res

    @api.onchange('bank_type')
    def onchange_bank_type(self):
        """当付款银行字段发生改变时，过滤付款账户。并赋默认值"""
        for res in self:
            res.public_account_id = False
            if res.bank_type:
                accs = self.env['bank.public.accounts'].sudo().search([('btype', '=', res.bank_type)])
                if accs:
                    res.public_account_id = accs[0]
                    res.DbProv = accs[0].abc_pc.id if accs[0].abc_pc else False
                domain = [('btype', '=', res.bank_type)]
                return {'domain': {'public_account_id': domain}}

    @api.multi
    def summit_payment(self):
        """开始向农业银行发送付款请求"""
        # 获取付款单对象
        payment = self.env['interface.bank.payment'].browse(self.env.context.get('active_id', False))
        for res in self:
            account = res.public_account_id
            str_xml = False
            if res.payment_type == 'a1':
                str_xml = self.pagk_group_exchange_panymeny_xml(account, res.pay_money, payment)
            elif res.payment_type == 'a2':
                str_xml = self.pagk_single_pen_panymeny_xml(account, res.pay_money, payment)
            elif res.payment_type == 'a3':
                str_xml = self.pagk_single_private_panymeny_xml(account, res.pay_money, payment)
            abc_ip = self.env['ir.values'].get_default('interface.bank.settings', 'abc_ip')
            abc_port = self.env['ir.values'].get_default('interface.bank.settings', 'abc_port')
            result_xml = abc_function.send_tcp(abc_ip, abc_port, str_xml)
            # 去掉xml头前面的7位数据长度格式
            logging.info(result_xml)
            result_xml = result_xml[7:]
            result_json = False
            # 解析xml
            try:
                result_json = json.dumps(xmltodict.parse(result_xml), indent=1)
                result_json = json.loads(result_json.strip())
            except ExpatError:
                payment_data = {
                    'bank_type': res.bank_type,
                    'public_account_id': res.public_account_id.id,
                    'payment_type': res.payment_type,
                }
                payment.write(payment_data)
                msg = u"由于网络原因,系统接收的数据包不完整！导致无法识别支付结果.请进行>异常交易查询<！"
                payment.message_post(body=msg, message_type='notification')
                return False
            ap = result_json['ap']
            # 判断结果码是否为'0000'
            if ap['RespCode'] == '0000':
                payment_data = {
                    'bank_type': res.bank_type,
                    'public_account_id': res.public_account_id.id,
                    'state': '02',
                    'payment_type': res.payment_type,
                }
                payment.write(payment_data)
                msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
                payment.message_post(body=msg, message_type='notification')
            else:
                msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
                payment.message_post(body=msg, message_type='notification')
                raise UserError(msg)

    @api.multi
    def pagk_group_exchange_panymeny_xml(self, account, pay_money, payment):
        """发起集团内-汇兑xml（CFRT01）
        :param account: 付款账户
        :param pay_money: 付款金额
        :param payment : 付款单对象
        :return string : 返回查询xml
        """
        logging.info(u"封装集团内-汇兑xml")
        # 企业操作员编号
        abc_operator_number = self.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
        # 认证码
        abc_auth_no = self.env['ir.values'].get_default('interface.bank.settings', 'abc_auth_no')
        # 数字签名
        abc_sign = self.env['ir.values'].get_default('interface.bank.settings', 'abc_sign')
        now_time = datetime.datetime.now()
        str_xml = {
            'CCTransCode': 'CFRT01',
            'ProductID': 'ICC',
            'ChannelType': 'ERP',
            'CorpNo': account.costomer_number,  # 企业技监局号码/客户号
            'OpNo': abc_operator_number,  # 企业操作员编号
            'AuthNo': abc_auth_no if abc_auth_no else '',  # 认证码
            'ReqSeqNo': payment.form_code,  # 请求方流水号
            'ReqDate': now_time.strftime('%Y%m%d'),
            'ReqTime': now_time.strftime('%H%M%S'),
            'Sign': abc_sign if abc_sign else '',
            'Amt': pay_money,  # 付款金额
            'Cmp': {
                'DbAccNo': account.payment_number,  # 借方账号
                'DbProv': self.DbProv.code,  # 借方省市代码
                'DbCur': payment.currency_type.number if payment.currency_type.number else '',  # 借方货币码
                'DbLogAccNo': '',  # 借方逻辑账号
                'CrProv': self.CrProv.code if self.CrProv else '',  # 贷方省市代码
                'CrAccNo': payment.partner_bank_number,  # 贷方账号
                'CrLogAccNo': '',  # 贷方逻辑账号
                'CrCur': payment.currency_type.number if payment.currency_type.number else '',  # 贷方货币码
                'ConFlag': '1' if self.conFlag else '0'  # 校验贷方户名标
            },
            'Corp': {
                'OthBankFlag': payment.cross_row_identi,  # 它行标志  默认为0
                'CrAccName': payment.partner_id,  # 收款方户名
                'DbAccName': account.payment_username,  # 付款方户名
                'WhyUse': payment.pay_use if payment.pay_use else '',  # 用途
                'Postscript': payment.pay_summary if payment.pay_use else ''  # 附言
            },
        }
        str_xml = abc_function.dict_to_xml('ap', str_xml)
        return tostring(str_xml)

    @api.multi
    def pagk_single_pen_panymeny_xml(self, account, pay_money, payment):
        """
        发起汇兑-单笔对公 xml (CFRT02交易)
        :param account:
        :param pay_money:
        :param payment:
        :return: string
        """
        if not payment.payee_bank_code:
            raise UserError(u"收款方归属银行（既行别）代码未输入！请维护！")
        logging.info(u"发起汇兑-单笔对公 xml")
        # 企业操作员编号
        abc_operator_number = self.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
        # 认证码
        abc_auth_no = self.env['ir.values'].get_default('interface.bank.settings', 'abc_auth_no')
        # 数字签名
        abc_sign = self.env['ir.values'].get_default('interface.bank.settings', 'abc_sign')
        now_time = datetime.datetime.now()
        if self.is_BookingFlag == '1':
            BookingTime = datetime.datetime.strptime(self.BookingTime, '%Y-%m-%d %H:%M:%S')
        str_xml = {
            'CCTransCode': 'CFRT02',
            'ProductID': 'ICC',
            'ChannelType': 'ERP',
            'CorpNo': account.costomer_number,  # 企业技监局号码/客户号
            'OpNo': abc_operator_number,  # 企业操作员编号
            'AuthNo': abc_auth_no if abc_auth_no else '',  # 认证码
            'ReqSeqNo': payment.form_code,  # 请求方流水号
            'ReqDate': now_time.strftime('%Y%m%d'),
            'ReqTime': now_time.strftime('%H%M%S'),
            'Sign': abc_sign if abc_sign else '',
            'Amt': pay_money,  # 付款金额
            'Cmp': {
                'DbProv': self.DbProv.code,  # 借方省市代码
                'DbAccNo': account.payment_number,  # 借方账号
                'DbLogAccNo': '',  # 借方逻辑账号
                'DbCur': payment.currency_type.number if payment.currency_type.number else '',  # 借方货币码
                'CrProv': self.CrProv.code if self.CrProv else '',  # 贷方省市代码  # 贷方省市代码
                'CrAccNo': payment.partner_bank_number,  # 贷方账号
                'CrLogAccNo': '',  # 贷方逻辑账号
                'CrCur': payment.currency_type.number if payment.currency_type.number else '',  # 贷方货币码
                'ConFlag': '1' if self.conFlag else '0'  # 校验贷方户名标识
            },
            'Corp': {
                'PsFlag': '',  # 一直为空
                'BookingFlag': self.is_BookingFlag,  # 预约标至 0 不预约 1预约
                'BookingDate': BookingTime.strftime('%Y%m%d') if self.is_BookingFlag == '1' else '',  # 预约日期
                'BookingTime': BookingTime.strftime('%H%M%S') if self.is_BookingFlag == '1' else '',  # 预约时点
                'UrgencyFlag': '1' if payment.payment_model == '02' else '0',  # 加急标志
                'OthBankFlag': payment.cross_row_identi,  # 它行标志  默认为0
                'CrBankType': payment.payee_bank_code if payment.payee_bank_code else '0',  # 它行行别
                'CrAccName': payment.partner_id,  # 收款方户名
                'CrBankName': payment.payee_opening_bank,  # 收款方开户行名
                'CrBankNo': payment.payee_opening_bank_code,  # 收款方开户行号
                'DbAccName': account.payment_username,  # 付款方户名
                'WhyUse': payment.pay_use if payment.pay_use else '',  # 用途
                'Postscript': payment.pay_summary if payment.pay_use else ''  # 附言
            },
        }
        str_xml = abc_function.dict_to_xml('ap', str_xml)
        return tostring(str_xml)

    @api.multi
    def pagk_single_private_panymeny_xml(self, account, pay_money, payment):
        """
        发起汇兑-单笔对私 xml (CFRT21交易)
        :param account:
        :param pay_money:
        :param payment:
        :return: string
        """
        logging.info(u"发起汇兑-单笔对私 xml")
        # 企业操作员编号
        abc_operator_number = self.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
        # 认证码
        abc_auth_no = self.env['ir.values'].get_default('interface.bank.settings', 'abc_auth_no')
        # 数字签名
        abc_sign = self.env['ir.values'].get_default('interface.bank.settings', 'abc_sign')
        now_time = datetime.datetime.now()
        if self.is_BookingFlag == '1':
            BookingTime = datetime.datetime.strptime(self.BookingTime, '%Y-%m-%d %H:%M:%S')
        str_xml = {
            'CCTransCode': 'CFRT21',
            'ProductID': 'ICC',
            'ChannelType': 'ERP',
            'CorpNo': account.costomer_number,  # 企业技监局号码/客户号
            'OpNo': abc_operator_number,  # 企业操作员编号
            'AuthNo': abc_auth_no if abc_auth_no else '',  # 认证码
            'ReqSeqNo': payment.form_code,  # 请求方流水号
            'ReqDate': now_time.strftime('%Y%m%d'),
            'ReqTime': now_time.strftime('%H%M%S'),
            'Sign': abc_sign if abc_sign else '',
            'Amt': pay_money,  # 付款金额
            'Cmp': {
                'DbProv': self.DbProv.code,  # 借方省市代码
                'DbAccNo': account.payment_number,  # 借方账号
                'DbLogAccNo': '',  # 借方逻辑账号
                'DbCur': payment.currency_type.number if payment.currency_type.number else '',  # 借方货币码
                'CrProv': self.CrProv.code,  # 贷方省市代码
                'CrAccNo': payment.partner_bank_number,  # 贷方账号
                'CrLogAccNo': '',  # 贷方逻辑账号
                'CrCur': payment.currency_type.number if payment.currency_type.number else '',  # 贷方货币码
                'ConFlag': '0'  # 校验贷方户名标
            },
            'Corp': {
                'PsFlag': '',  # 一直为空
                'BookingFlag': self.is_BookingFlag,  # 预约标至 0 不预约 1预约
                'BookingDate': BookingTime.strftime('%Y%m%d') if self.is_BookingFlag == '1' else '',  # 预约日期
                'BookingTime': BookingTime.strftime('%H%M%S') if self.is_BookingFlag == '1' else '',  # 预约时点
                'UrgencyFlag': '0',  # 加急标志
                'OthBankFlag': payment.cross_row_identi,  # 它行标志  默认为0
                'CrAccName': payment.partner_id,  # 收款方户名
                'DbAccName': account.payment_username,  # 付款方户名
                'WhyUse': payment.pay_use if payment.pay_use else '',  # 用途
                'Postscript': payment.pay_summary if payment.pay_use else ''  # 附言
            },
        }
        str_xml = abc_function.dict_to_xml('ap', str_xml)
        return tostring(str_xml)


# 签发银行汇票
class ABCBankDraft(models.Model):
    _description = u"签发银行汇票"
    _name = 'interface.abc.bank.draft'
    _inherit = 'mail.thread'
    _rec_name = 'form_code'

    BillType = [
        ('1', u'全国'),
        ('2', u'省辖'),
        ('3', u'县辖'),
        ('4', u'华东三省一市汇票作全国'),
        ('5', u'华东三省一市汇票作省辖'),
        ('6', u'华东三省一市汇票作县辖'),
    ]
    PSTATE = [
        ('00', u'草稿'),
        ('01', u'银行确认'),
        ('02', u'成功'),
        ('03', u'失败')
    ]
    form_code = fields.Char(string=u'交易识别号')
    company_id = fields.Many2one(comodel_name='res.company', string=u'签发公司')
    public_account_id = fields.Many2one(comodel_name='bank.public.accounts', string=u'付款账户', required=True,
                                        domain=[('btype', '!=', '00')])
    DbProv = fields.Many2one(comodel_name='interface.abc.province.city', string=u'付款省市', required=True)
    currency_type = fields.Many2one(string=u'交易币种', comodel_name='bank.currency', required=True)
    receipt = fields.Char(string=u'收款名称', required=True)
    receipt_number = fields.Char(string=u'收款账号', required=True)
    bill_type = fields.Selection(string=u'票汇种类', selection=BillType, default='1')
    cash_flag = fields.Selection(string=u'现转标志', selection=[('0', u'现金'), ('1', u'转账'), ], default='1')
    draft_flag = fields.Selection(string=u'转让标志', selection=[('0', u'不可转让'), ('1', u'可转让'), ], default='0')
    pay_summary = fields.Char(string=u'摘要')
    pay_use = fields.Text(string=u'付款用途')
    pay_money = fields.Float(string=u'签发金额', digits=(23, 2))
    state = fields.Selection(string=u'单据状态', selection=PSTATE, default=u'00')
    withdraw_password = fields.Char(string=u'支取密码')

    @api.onchange('public_account_id')
    def onchange_public_account_id(self):
        """付款账户赋默认值"""
        for res in self:
            if res.public_account_id:
                res.DbProv = res.public_account_id.abc_pc.id if res.public_account_id.abc_pc else False

    @api.model
    def create(self, vals):
        if vals['pay_money'] <= 0:
            raise UserError(u"签发金额不能小于等于0！")
        if not vals['form_code']:
            vals['form_code'] = self.env['ir.sequence'].sudo().next_by_code('interface.abc.bank.draft.number')
        return super(ABCBankDraft, self).create(vals)

    @api.multi
    def start_bank_issue(self):
        """签发银行汇票功能"""
        for res in self:
            logging.info(u'签发银行汇票功能')
            str_xml = self.pagk_bank_issue_xml()
            abc_ip = self.env['ir.values'].get_default('interface.bank.settings', 'abc_ip')
            abc_port = self.env['ir.values'].get_default('interface.bank.settings', 'abc_port')
            result_xml = abc_function.send_tcp(abc_ip, abc_port, str_xml)
            # 去掉xml头前面的7位数据长度格式
            logging.info(result_xml)
            result_xml = result_xml[7:]
            # 解析xml
            try:
                result_json = json.dumps(xmltodict.parse(result_xml), indent=1)
                result_json = json.loads(result_json.strip())
            except ExpatError:
                msg = u"由于网络原因,系统接收的数据包不完整！导致无法识别支付结果,请试着查询余额看是否已支出！或查询落地结果"
                res.message_post(body=msg, message_type='notification')
                raise UserError(msg)
            ap = result_json['ap']
            # 判断结果码是否为'0000'
            if ap['RespCode'] == '0000':
                Cmp = ap['Cmp']
                issue_data = {
                    'state': '02',
                    'withdraw_password': Cmp['TransPwd'],
                }
                res.write(issue_data)
                msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
                res.message_post(body=msg, message_type='notification')
            else:
                msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
                res.message_post(body=msg, message_type='notification')
                raise UserError(msg)

    @api.multi
    def pagk_bank_issue_xml(self):
        """封装xml  CFRT17
        :return string : xml
        """
        for res in self:
            logging.info(u'封装签发银行汇票功能xml')
            # 企业操作员编号
            abc_operator_number = self.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
            # 认证码
            abc_auth_no = self.env['ir.values'].get_default('interface.bank.settings', 'abc_auth_no')
            # 数字签名
            abc_sign = self.env['ir.values'].get_default('interface.bank.settings', 'abc_sign')
            now_time = datetime.datetime.now()
            str_xml = {
                'CCTransCode': 'CFRT17',
                'ProductID': 'ICC',
                'ChannelType': 'ERP',
                'CorpNo': res.public_account_id.costomer_number,  # 企业技监局号码/客户号
                'OpNo': abc_operator_number,  # 企业操作员编号
                'AuthNo': abc_auth_no if abc_auth_no else '',  # 认证码
                'ReqSeqNo': res.form_code,  # 请求方流水号
                'ReqDate': now_time.strftime('%Y%m%d'),
                'ReqTime': now_time.strftime('%H%M%S'),
                'Sign': abc_sign if abc_sign else '',
                'Amt': res.pay_money,  # 付款金额
                'Cmp': {
                    'DbLogAccNo': '',  # 借方逻辑账薄
                    'DbProv': res.DbProv.code,  # 借方省市代码
                    'DbAccNo': res.public_account_id.payment_number,  # 借方账号
                    'DbCur': '01',  # 借方货币码
                    'CrAccNo': res.receipt_number,  # 贷方账号
                    'CrCur': '01',  # 贷方货币码
                },
                'Corp': {
                    'BillType': res.bill_type if res.bill_type else '1',  # 汇票种类
                    'CashFlag': res.cash_flag if res.cash_flag else '1',  # 现转标志
                    'DraftFlag': res.draft_flag if res.draft_flag else '0',  # 转让标志
                    'DbAccName': res.public_account_id.payment_username,  # 付款人名称
                    'CrAccName': res.receipt,  # 收款人名称
                    'WhyUse': res.pay_use if res.pay_use else '',  # 用途
                    'Postscript': res.pay_summary if res.pay_use else '',  # 附言
                    'AgtCrInd': '0'  # 集中代理收付标志
                },
            }
            str_xml = abc_function.dict_to_xml('ap', str_xml)
            return tostring(str_xml)

    @api.multi
    def get_withdraw_password(self):
        """获取支取密码"""
        for res in self:
            if res.withdraw_password:
                msg = u"""该汇票的支取密码为:  {}""".format(res.withdraw_password)
                res.message_post(body=u"已获取了支取密码!", message_type='notification')
                raise UserError(msg)
            else:
                raise UserError(u"该汇票未发生,故无法提供支取密码！")


# 实时代付
class ABCRealtimePayment(models.TransientModel):
    _description = u"实时代付"
    _name = 'interface.abc.realtime.payment'

    account_id = fields.Many2one(comodel_name='bank.public.accounts', string=u'付款账户', domain=[('btype', '!=', '00')],
                                 required=True)
    DbProv = fields.Many2one(comodel_name='interface.abc.province.city', string=u'付款省市', required=True)
    currency_id = fields.Many2one(comodel_name='bank.currency', string=u'付款方币种', required=True)
    partner_bank_number = fields.Char(string=u'收款账号', required=True)
    CrProv = fields.Many2one(comodel_name='interface.abc.province.city', string=u'收款省市', required=True)
    CrCur = fields.Many2one(comodel_name='bank.currency', string=u'收款方币种', required=True)
    ConFlag = fields.Selection(string=u'合约校验', selection=[('0', u'不校验'), ('1', u'校验')], default='0')
    CheckNameFlag = fields.Selection(string=u'户名校验', selection=[('0', u'不校验'), ('1', u'校验')], default='0')
    PayInt = fields.Selection(string=u'收费标志', selection=[('0', u'不收费'), ('1', u'收费')], default='0')
    AgtDbInd = fields.Selection(string=u'集中代理支付标志', selection=[('0', u'不代理'), ('1', u'代理')], default='0')
    NVoucherType = fields.Selection(string=u'合约类型',
                                    selection=[
                                        ('020001', u'工资发放'),
                                        ('020002', u'费用报销'),
                                        ('020003', u'代付保费'),
                                        ('029999', u'代付其他'),
                                    ],
                                    default='020001')
    CshDraFlag = fields.Selection(string=u'钞汇标志', selection=[('0', u'钞'), ('1', u'汇')], default='0')
    Amt = fields.Char(string=u'金额', required=True)

    @api.onchange('account_id')
    def onchange_account_id(self):
        """付款账户赋默认值"""
        for res in self:
            res.account_id = False
            accs = self.env['bank.public.accounts'].sudo().search([('btype', '!=', '00')])
            if accs:
                res.account_id = accs[0]
                res.DbProv = accs[0].abc_pc.id if accs[0].abc_pc else False

    @api.model
    def default_get(self, fields):
        """获取默认值"""
        res = super(ABCRealtimePayment, self).default_get(fields)
        payment_id = self.env.context.get('active_id', False)
        payment = self.env['interface.bank.payment'].browse(payment_id)
        if payment:
            if 'partner_bank_number' in fields:
                res.update({'partner_bank_number': payment.partner_bank_number})
            if 'CrCur' in fields:
                res.update({'CrCur': payment.currency_type.id})
            if 'currency_id' in fields:
                res.update({'currency_id': payment.currency_type.id})
            if 'Amt' in fields:
                res.update({'Amt': payment.pay_money})
            return res

    @api.multi
    def summit_payment(self):
        """实时代付"""
        # 获取付款单对象
        payment = self.env['interface.bank.payment'].browse(self.env.context.get('active_id', False))
        for res in self:
            str_xml = self.pack_xml(payment)
            logging.info(str_xml)
            abc_ip = self.env['ir.values'].get_default('interface.bank.settings', 'abc_ip')
            abc_port = self.env['ir.values'].get_default('interface.bank.settings', 'abc_port')
            result_xml = abc_function.send_tcp(abc_ip, abc_port, str_xml)
            # 去掉xml头前面的7位数据长度格式
            logging.info(result_xml)
            result_xml = result_xml[7:]
            result_json = False
            # 解析xml
            try:
                result_json = json.dumps(xmltodict.parse(result_xml), indent=1)
                result_json = json.loads(result_json.strip())
            except ExpatError:
                payment_data = {
                    'bank_type': '01',
                    'public_account_id': res.account_id.id,
                    'payment_type': 's1',
                }
                payment.write(payment_data)
                msg = u"由于网络原因,系统接收的数据包不完整！导致无法识别支付结果.\r\n请试着查询余额看是否已支出！或查询异常交易(推荐)！"
                payment.message_post(body=msg, message_type='notification')
                # 创建实时代付日志记录
                self.create_realtime_payment_log(payment)
                return False
            ap = result_json['ap']
            # 判断结果码是否为'0000'
            if ap['RespCode'] == '0000':
                payment_data = {
                    'bank_type': '01',
                    'public_account_id': res.account_id.id,
                    'payment_type': 's1',
                }
                payment.write(payment_data)
                msg = "{};\r\n{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
                payment.message_post(body=msg, message_type='notification')
                # 创建实时代付日志记录
                self.create_realtime_payment_log(payment)
            else:
                msg = "{};\r\n{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
                payment.message_post(body=msg, message_type='notification')
                raise UserError(msg)

    @api.multi
    def pack_xml(self, payment):
        """封装xml"""
        for res in self:
            # 企业操作员编号
            abc_operator_number = self.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
            # 认证码
            abc_auth_no = self.env['ir.values'].get_default('interface.bank.settings', 'abc_auth_no')
            # 数字签名
            abc_sign = self.env['ir.values'].get_default('interface.bank.settings', 'abc_sign')
            now_time = datetime.datetime.now()
            str_xml = {
                'CCTransCode': 'CFRTD1',
                'ProductID': 'ICC',
                'ChannelType': 'ERP',
                'CorpNo': res.account_id.costomer_number,  # 企业技监局号码/客户号
                'OpNo': abc_operator_number if abc_operator_number else '',  # 企业操作员编号
                'AuthNo': abc_auth_no if abc_auth_no else '',  # 认证码
                'ReqSeqNo': payment.form_code,  # 请求方流水号
                'ReqDate': now_time.strftime('%Y%m%d'),
                'ReqTime': now_time.strftime('%H%M%S'),
                'Sign': abc_sign if abc_sign else '',
                'Cmp': {
                    'DbAccNo': res.account_id.payment_number,  # 付款方账号
                    'DbProv': res.DbProv.code,  # 付款方省市代码
                    'DbCur': res.currency_id.number,  # 付款方币种
                    'CrAccNo': res.partner_bank_number,  # 收款方账号
                    'CrProv': res.CrProv.code,  # 收款方省市代码
                    'CrCur': res.CrCur.number,  # 收款方币种
                    'ConFlag': res.ConFlag,
                    'CheckNameFlag': res.CheckNameFlag,
                },
                'Corp': {
                    'PayInt': res.PayInt,
                    'AgtDbInd': res.AgtDbInd,
                    'NVoucherType': res.NVoucherType,  # 合约类型
                    'CshDraFlag': res.CshDraFlag,
                },
                'Amt': res.Amt
            }
            str_xml = abc_function.dict_to_xml('ap', str_xml)
            return tostring(str_xml)

    @api.multi
    def create_realtime_payment_log(self, payment):
        """创建实时代付日志记录"""
        for res in self:
            self.env['abc.realtime.payment.line'].create({
                'payment': payment.id,
                'account_id': res.account_id.id,
                'currency_id': res.currency_id.id,
                'partner_bank_number': res.partner_bank_number,
                'CrProv': res.CrProv,
                'CrCur': res.CrCur.id,
                'ConFlag': res.ConFlag,
                'CheckNameFlag': res.CheckNameFlag,
                'PayInt': res.PayInt,
                'AgtDbInd': res.AgtDbInd,
                'NVoucherType': res.NVoucherType,
                'CshDraFlag': res.CshDraFlag,
                'Amt': res.Amt,
            })


class ABCRealtimePaymentLine(models.Model):
    _description = u"实时代付记录"
    _name = 'abc.realtime.payment.line'
    _inherit = 'interface.abc.realtime.payment'
    _rec_name = 'payment'

    payment = fields.Many2one(comodel_name='interface.bank.payment', string=u'付款单')


# 代发工资
class ABCWagesOnBehalfOf(models.Model):
    _description = u"代发工资"
    _name = 'interface.abc.wages.behalf'
    _inherit = 'mail.thread'
    _rec_name = 'form_code'

    form_code = fields.Char(string=u'单据流水号')
    account_id = fields.Many2one(comodel_name='bank.public.accounts', string=u'付款账户', domain=[('btype', '!=', '00')],
                                 required=True)
    DbProv = fields.Many2one(comodel_name='interface.abc.province.city', string=u'付款省市', required=True)
    currency_id = fields.Many2one(comodel_name='bank.currency', string=u'交易币种币种', required=True)
    Amt = fields.Float(string=u'交易总金额', digits=(23, 3))
    number = fields.Integer(string=u'交易总笔数')
    Postscript = fields.Text(string=u'附言')
    state = fields.Selection(string=u'状态', selection=[(u'00', u'草稿'), ('01', u'已发送'), ], default='00')
    line_ids = fields.One2many(comodel_name='interface.abc.wages.behalf.line', inverse_name='behalf_id', string=u'列表')

    @api.onchange('account_id')
    def onchange_account_id(self):
        """付款账户赋默认值"""
        for res in self:
            if res.account_id:
                res.DbProv = res.account_id.abc_pc.id if res.account_id.abc_pc else False

    @api.onchange('line_ids')
    def onchange_line_ids(self):
        """动态获取交易总金额和总笔数"""
        if self.line_ids:
            amt_sum = 0
            for line in self.line_ids:
                amt_sum = amt_sum + line.amt
            self.Amt = amt_sum
            self.number = len(self.line_ids)

    @api.model
    def create(self, vals):
        if not vals['form_code']:
            vals['form_code'] = self.env['ir.sequence'].sudo().next_by_code('abc.wages.behalf.number')
        return super(ABCWagesOnBehalfOf, self).create(vals)

    @api.multi
    def start_bank_issue(self):
        """确认工资信息并发送至农行系统"""
        for res in self:
            # 封装ffs文件
            filename = self.pack_wages_file()
            # 利用ftp上传文件到前置机
            abc_function.up_ftp_file(filename)
            # 封装xml通知前置机处理文件
            xml_filename = self.pack_xml(filename)
            str_xml = abc_function.read_local_file(xml_filename)
            # 开始上传xml
            abc_ip = self.env['ir.values'].get_default('interface.bank.settings', 'abc_ip')
            abc_port = self.env['ir.values'].get_default('interface.bank.settings', 'abc_port')
            result_xml = abc_function.send_wages_xml(abc_ip, abc_port, str_xml)
            # 去掉xml头前面的7位数据长度格式
            logging.info(result_xml)
            result_xml = result_xml[7:]
            # 解析xml
            try:
                result_json = json.dumps(xmltodict.parse(result_xml), indent=1)
                result_json = json.loads(result_json.strip())
            except ExpatError:
                msg = u"由于网络原因,系统接收的数据包不完整！导致无法识别支付结果,请试着查询余额看是否已支出！或查询落地交易结果"
                res.message_post(body=msg, message_type='notification')
                raise UserError(msg)
            ap = result_json['ap']
            # 判断结果码是否为'0000'
            if ap['RespCode'] == '0000':
                issue_data = {
                    'state': '01',
                }
                res.write(issue_data)
                msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
                res.message_post(body=msg, message_type='notification')
            else:
                msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
                res.message_post(body=msg, message_type='notification')
                raise UserError(msg)

    @api.multi
    def pack_wages_file(self):
        """封装工资文件
        :return 文件名
        """
        # 判断目录是否存在
        import os
        if not os.path.exists("AbcData"):
            logging.info(u"文件目录AbcData不存在！系统将新建！")
            if not os.path.isdir("AbcData"):
                os.mkdir("AbcData")
        # 企业操作员编号
        abc_operator_number = self.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
        filename = '{}.{}_{}.{}'.format(self.form_code, self.account_id.costomer_number, abc_operator_number,
                                        abc_function.get_strftime())
        wage_file = io.open("AbcData/" + filename, 'wb')
        for line in self.line_ids:
            line_name = abc_function.supplement_string_length(line.name, 60)
            line_customer_number = abc_function.supplement_string_length(line.customer_number, 30)
            line_amt = abc_function.supplement_amt_length(line.amt, 18)
            line_postscript = abc_function.supplement_string_length(line.postscript, 30)
            str_data = '{}{}{}{}\n'.format(line_name, line_customer_number, line_amt, line_postscript)
            wage_file.writelines(str_data.encode(encoding='gbk'))
        wage_file.close()
        return filename

    @api.multi
    def pack_xml(self, filename):
        """封装xml CFRT03"""
        for res in self:
            # xml文件名称
            xml_filename = "AbcData/CFRT03.xml"
            # 企业操作员编号
            abc_operator_number = self.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
            # 认证码
            abc_auth_no = self.env['ir.values'].get_default('interface.bank.settings', 'abc_auth_no')
            # 数字签名
            abc_sign = self.env['ir.values'].get_default('interface.bank.settings', 'abc_sign')
            now_time = datetime.datetime.now()
            from xml.etree.ElementTree import Element, SubElement, ElementTree
            ap = Element('ap')
            CCTransCode = SubElement(ap, 'CCTransCode')
            CCTransCode.text = 'CFRT03'
            ProductID = SubElement(ap, 'ProductID')
            ProductID.text = 'ICC'
            ChannelType = SubElement(ap, 'ChannelType')
            ChannelType.text = 'ERP'
            CorpNo = SubElement(ap, 'CorpNo')
            CorpNo.text = res.account_id.costomer_number
            OpNo = SubElement(ap, 'OpNo')
            OpNo.text = abc_operator_number
            AuthNo = SubElement(ap, 'AuthNo')
            AuthNo.text = abc_auth_no if abc_auth_no else ''
            ReqSeqNo = SubElement(ap, 'ReqSeqNo')
            ReqSeqNo.text = res.form_code
            ReqDate = SubElement(ap, 'ReqDate')
            ReqDate.text = now_time.strftime('%Y%m%d')
            ReqTime = SubElement(ap, 'ReqTime')
            ReqTime.text = now_time.strftime('%H%M%S')
            Sign = SubElement(ap, 'Sign')
            Sign.text = abc_sign if abc_sign else ''
            Amt = SubElement(ap, 'Amt')
            Amt.text = str(res.Amt)  # 付款金额
            FileFlag = SubElement(ap, 'FileFlag')
            FileFlag.text = '1'
            # cmp
            Cmp = SubElement(ap, 'Cmp')
            DbProv = SubElement(Cmp, 'DbProv')
            DbProv.text = res.DbProv.code  # 借方省市代码
            DbAccNo = SubElement(Cmp, 'DbAccNo')
            DbAccNo.text = res.account_id.payment_number  # 借方账号
            DbCur = SubElement(Cmp, 'DbCur')
            DbCur.text = res.currency_id.number  # 借方货币码
            BatchFileName = SubElement(Cmp, 'BatchFileName')
            BatchFileName.text = filename  # 代发工资文件名
            # Corp
            Corp = SubElement(ap, 'Corp')
            DbAccName = SubElement(Corp, 'DbAccName')
            DbAccName.text = res.account_id.payment_username  # 借方户名
            Postscript = SubElement(Corp, 'Postscript')
            Postscript.text = res.Postscript if res.Postscript else ''  # 附言
            # Cme
            Cme = SubElement(ap, 'Cme')
            InterBusFlag = SubElement(Cme, 'InterBusFlag')
            InterBusFlag.text = '1'  # 默认为1
            # Tulip
            Tulip = SubElement(ap, 'Tulip')
            pcl = SubElement(Tulip, u'批处理')
            pamt = SubElement(pcl, u'批交易总金额')
            pamt.text = str(res.Amt)  # 批交易总金额
            pnumber = SubElement(pcl, u'批交易总笔数')
            pnumber.text = str(res.number)  # 批交易总笔数
            # 封装tree
            tree = ElementTree(ap)
            tree.write(xml_filename, encoding='utf-8')
            return xml_filename


class ABCWagesOnBehalfOfLine(models.Model):
    _name = 'interface.abc.wages.behalf.line'
    _rec_name = 'behalf_id'
    _description = u'代发工资列表'

    name = fields.Char(string=u'姓名', required=True)
    customer_number = fields.Char(string=u'客户账号\卡号', required=True)
    amt = fields.Float(string=u'交易金额', digits=(23, 3), required=True)
    postscript = fields.Char(string=u'备注')
    behalf_id = fields.Many2one(comodel_name='interface.abc.wages.behalf', string=u'代发工资', ondelete='cascade')


# 费用报销
class AbcReimbursement(models.Model):
    _name = 'interface.abc.reimbur.sement'
    _description = u"费用报销"
    _inherit = 'mail.thread'
    _rec_name = 'form_code'

    form_code = fields.Char(string=u'单据流水号')
    account_id = fields.Many2one(comodel_name='bank.public.accounts', string=u'付款账户', domain=[('btype', '!=', '00')],
                                 required=True)
    currency_id = fields.Many2one(comodel_name='bank.currency', string=u'交易币种', required=True)
    amt = fields.Float(string=u'报销总金额', digits=(23, 3))
    number = fields.Integer(string=u'报销总笔数')
    postscript = fields.Text(string=u'附言')
    state = fields.Selection(string=u'状态', selection=[(u'00', u'草稿'), ('01', u'已发送'), ], default='00')
    line_ids = fields.One2many(comodel_name='interface.abc.reimbur.sement.line', inverse_name='sement_id', string=u'列表')
    sement_name = fields.Char(string=u'报销人姓名', required=True)
    sement_no = fields.Char(string=u'报销人账号\卡号', required=True)
    sement_currency_id = fields.Many2one(comodel_name='bank.currency', string=u'报销币种', required=True)
    pc_id = fields.Many2one(comodel_name='interface.abc.province.city', string=u'省市代码', required=True)

    @api.onchange('line_ids')
    def onchange_line_ids(self):
        """动态获取交易总金额和总笔数"""
        if self.line_ids:
            amt_sum = 0
            for line in self.line_ids:
                amt_sum = amt_sum + line.amt
            self.amt = amt_sum
            self.number = len(self.line_ids)

    @api.model
    def create(self, vals):
        if not vals['form_code']:
            vals['form_code'] = self.env['ir.sequence'].sudo().next_by_code('interface.abc.reimbur.sement')
        return super(AbcReimbursement, self).create(vals)

    @api.multi
    def start_bank_issue(self):
        """发送报销信息"""
        for res in self:
            # 封装ffs文件
            filename = self.pack_sement_file()
            # 利用ftp上传文件到前置机
            abc_function.up_ftp_file(filename)
            # 封装xml通知前置机处理文件
            xml_filename = self.pack_xml(filename)
            str_xml = abc_function.read_local_file(xml_filename)
            # 开始上传xml
            abc_ip = self.env['ir.values'].get_default('interface.bank.settings', 'abc_ip')
            abc_port = self.env['ir.values'].get_default('interface.bank.settings', 'abc_port')
            result_xml = abc_function.send_wages_xml(abc_ip, abc_port, str_xml)
            # 去掉xml头前面的7位数据长度格式
            logging.info(result_xml)
            result_xml = result_xml[7:]
            # 解析xml
            try:
                result_json = json.dumps(xmltodict.parse(result_xml), indent=1)
                result_json = json.loads(result_json.strip())
            except ExpatError:
                msg = u"由于网络原因,系统接收的数据包不完整！导致无法识别支付结果,请试着查询余额看是否已支出！或查询落地交易结果"
                res.message_post(body=msg, message_type='notification')
                raise UserError(msg)
            ap = result_json['ap']
            # 判断结果码是否为'0000'
            if ap['RespCode'] == '0000':
                res.write({'state': '01'})
                msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
                res.message_post(body=msg, message_type='notification')
            else:
                msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
                res.message_post(body=msg, message_type='notification')
                raise UserError(msg)

    @api.multi
    def pack_xml(self, filename):
        for res in self:
            # xml文件名称
            xml_filename = "AbcData/CFRT05.xml"
            # 企业操作员编号
            abc_operator_number = self.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
            # 认证码
            abc_auth_no = self.env['ir.values'].get_default('interface.bank.settings', 'abc_auth_no')
            # 数字签名
            abc_sign = self.env['ir.values'].get_default('interface.bank.settings', 'abc_sign')
            now_time = datetime.datetime.now()
            from xml.etree.ElementTree import Element, SubElement, ElementTree
            ap = Element('ap')
            CCTransCode = SubElement(ap, 'CCTransCode')
            CCTransCode.text = 'CFRT03'
            ProductID = SubElement(ap, 'ProductID')
            ProductID.text = 'ICC'
            ChannelType = SubElement(ap, 'ChannelType')
            ChannelType.text = 'ERP'
            CorpNo = SubElement(ap, 'CorpNo')
            CorpNo.text = res.account_id.costomer_number
            OpNo = SubElement(ap, 'OpNo')
            OpNo.text = abc_operator_number
            AuthNo = SubElement(ap, 'AuthNo')
            AuthNo.text = abc_auth_no if abc_auth_no else ''
            ReqSeqNo = SubElement(ap, 'ReqSeqNo')
            ReqSeqNo.text = res.form_code
            ReqDate = SubElement(ap, 'ReqDate')
            ReqDate.text = now_time.strftime('%Y%m%d')
            ReqTime = SubElement(ap, 'ReqTime')
            ReqTime.text = now_time.strftime('%H%M%S')
            Sign = SubElement(ap, 'Sign')
            Sign.text = abc_sign if abc_sign else ''
            Amt = SubElement(ap, 'Amt')
            Amt.text = str(res.amt)  # 付款金额
            FileFlag = SubElement(ap, 'FileFlag')  # 是否上传文件
            FileFlag.text = '1'
            # 'Cmp'
            Cmp = SubElement(ap, 'Cmp')
            DbProv = SubElement(Cmp, 'DbProv')
            DbProv.text = '22'  # 借方省市代码
            DbAccNo = SubElement(Cmp, 'DbAccNo')
            DbAccNo.text = res.account_id.payment_number  # 借方账号
            DbCur = SubElement(Cmp, 'DbCur')
            DbCur.text = res.currency_id.number  # 借方货币码
            CrProv = SubElement(Cmp, 'CrProv')
            CrProv.text = res.pc_id.code  # 省市代码
            CrAccNo = SubElement(Cmp, 'CrAccNo')
            CrAccNo.text = res.sement_no  # 账号
            CrCur = SubElement(Cmp, 'CrCur')
            CrCur.text = res.sement_currency_id.number  # 账号币种
            BatchFileName = SubElement(Cmp, 'BatchFileName')
            BatchFileName.text = filename  # 代发工资文件名
            # Corp
            Corp = SubElement(ap, 'Corp')
            DbAccName = SubElement(Corp, 'DbAccName')
            DbAccName.text = res.account_id.payment_username  # 借方户名
            Postscript = SubElement(Corp, 'Postscript')
            Postscript.text = res.postscript if res.postscript else ''  # 附言
            # Cme
            Cme = SubElement(ap, 'Cme')
            InterBusFlag = SubElement(Cme, 'InterBusFlag')
            InterBusFlag.text = '2'  # 默认为2
            # Tulip
            Tulip = SubElement(ap, 'Tulip')
            pcl = SubElement(Tulip, u'批处理')
            pamt = SubElement(pcl, u'批交易总金额')
            pamt.text = str(res.amt)  # 批交易总金额
            pnumber = SubElement(pcl, u'批交易总笔数')
            pnumber.text = str(res.number)  # 批交易总笔数
            # 封装tree
            tree = ElementTree(ap)
            tree.write(xml_filename, encoding='utf-8')
            return xml_filename

    @api.multi
    def pack_sement_file(self):
        """封装文件
        :return 文件名
       """
        # 判断目录是否存在
        import os
        if not os.path.exists("AbcData"):
            logging.info(u"文件目录AbcData不存在！系统将新建！")
            if not os.path.isdir("AbcData"):
                os.mkdir("AbcData")
        # 企业操作员编号
        abc_operator_number = self.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
        filename = '{}.{}_{}.{}'.format(self.form_code, self.account_id.costomer_number, abc_operator_number,
                                        abc_function.get_strftime())
        wage_file = io.open("AbcData/" + filename, 'wb')
        c_name = abc_function.supplement_string_length(self.sement_name, 60)
        c_number = abc_function.supplement_string_length(self.sement_no, 30)
        for line in self.line_ids:
            line_amt = abc_function.supplement_amt_length(line.amt, 18)
            line_postscript = abc_function.supplement_string_length(line.postscript, 30)
            str_data = "{}{}{}{}\n".format(c_name, c_number, line_amt, line_postscript)
            wage_file.writelines(str_data.encode(encoding='gbk'))
        wage_file.close()
        return filename


# 费用报销子表
class AbcReimbursementLine(models.Model):
    _description = u"费用报销子表"
    _name = 'interface.abc.reimbur.sement.line'

    sement_id = fields.Many2one(comodel_name='interface.abc.reimbur.sement', string=u'费用', ondelete='cascade')
    amt = fields.Float(string=u'交易金额', digits=(23, 3), required=True)
    postscript = fields.Char(string=u'报销说明')


# 拓展付款单
class AbcPaymentInherit(models.Model):
    _inherit = 'interface.bank.payment'
    _description = u"银行付款单"

    payment_type = fields.Selection(selection_add=[('s1', u'实时代付')])

    @api.multi
    def search_transaction(self):
        """
        添加支付失败时，调用农行查询异常交易函数手动查询交易结果
        :return: boolean
        """
        for res in self:
            logging.info(u">>>开始手动执行查询异常交易结果,代码编号:{}".format(res.form_code))
            str_xml = self.env['interface.abc.abnormal.transaction'].pack_search_abnormal_transaction_xml(
                res.public_account_id, res.currency_type, res)
            logging.info(str_xml)
            abc_ip = self.env['ir.values'].get_default('interface.bank.settings', 'abc_ip')
            abc_port = self.env['ir.values'].get_default('interface.bank.settings', 'abc_port')
            result_xml = abc_function.send_tcp(abc_ip, abc_port, str_xml)
            logging.info(result_xml)
            result_xml = result_xml[7:]
            # 解析xml
            try:
                result_json = json.dumps(xmltodict.parse(result_xml), indent=1)
                result_json = json.loads(result_json.strip())
            except ExpatError:
                msg = u"由于网络原因,系统接收到的数据包不完整！导致无法识别结果,请重试!"
                raise UserError(msg)
            ap = result_json['ap']
            # 判断结果码是否为'0000'
            if ap['RespCode'] == '0000':
                Cmp = ap['Cmp']
                Corp = ap['Corp']
                # 获取返回码
                RespPrvData = Cmp['RespPrvData']
                if RespPrvData[-4:] == '0000':
                    res.write({'state': '02'})
                    res.message_post(body=ap['RespInfo'], message_type='notification')
                else:
                    res.message_post(body=Corp['Postscript'], message_type='notification')
            else:
                msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
                raise UserError(msg)
