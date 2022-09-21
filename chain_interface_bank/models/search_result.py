# -*- coding: utf-8 -*-
import json

from pyexpat import ExpatError

from odoo import models, api, fields
import logging
from odoo.exceptions import UserError
from cqt_functions import CqtFunction as cqt
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
_logger = logging.getLogger(__name__)


# 查询付款单结果
class SearchPaymentResult(models.TransientModel):
    _name = 'interface.search.payment.res'
    _description = u"查询付款单结果"

    @api.model
    def search_payment_result(self, payment_from_number):
        """根据查询付款单的编号查询银行付款处理结果
        :param payment_from_number: 付款单编号可多个，用英文逗号隔开
        """
        logging.info(u"查询的付款单据编码为：%s" % payment_from_number)
        number_arrays = payment_from_number.split(',')
        for number in number_arrays:
            payment = self.env['interface.bank.payment'].sudo().search([('form_code', '=', number)])
            if len(payment) != 1:
                raise UserError(u"付款单据编号：%s不存在！" % number)
        # 将付款单据编号封装成xml
        xml_str = cqt.package_query_payment_result_to_xml(number_arrays)
        # 获取财企通前置机地址url
        service_url = self.env['ir.values'].get_default('interface.bank.settings', 'feg_add')
        # 将xml字符串发送到财企通并接受结果xml
        result_xml = cqt.send_xml_to_cqtbankservice(xml_str, service_url)
        # 解析xml
        result_json = cqt.xml_to_json(result_xml)
        result_json = json.loads(result_json.strip())
        efmp = result_json['efmp']
        body = efmp['body']
        result_set = body['resultSet']
        # 封装结果返回到页面
        result_list = list()
        result = result_set['result']
        if isinstance(result, dict):
            try:
                data = {
                    'payment_from_code': result['requestId'],
                    'state_code': result['cmdStatus'],
                    'result_code': result['resultCode'],
                    'message': result['resultMsg'],
                }
                result_list.append(data)
            except KeyError:
                data = {
                    'result_code': result['resultCode'],
                    'message': result['resultMsg'],
                }
                result_list.append(data)
        elif isinstance(result, list):
            for res in result:
                data = {
                    'payment_from_code': res['requestId'],
                    'state_code': res['cmdStatus'],
                    'result_code': res['resultCode'],
                    'message': res['resultMsg'],
                }
                result_list.append(data)
        return result_list


# 查询电子回单结果表
class SearchElectronicReceiptResult(models.Model):
    _name = 'interface.bank.electronic.receipt.result'
    _description = u"查询电子回单结果表"
    _rec_name = 'custNo'

    custNo = fields.Char(string=u'客户编号')
    custName = fields.Char(string=u'客户名称')
    slipId = fields.Char(string=u'电子回单ID')
    slipNo = fields.Char(string=u'电子回单号')
    startDate = fields.Date(string=u'开始日期')
    endDate = fields.Date(string=u'结束日期')
    total = fields.Char(string=u'记录总数')
    packageId = fields.Char(string=u'报文标识号')
    resultCode = fields.Char(string=u'结果码')
    resultMsg = fields.Char(string=u'结果信息')
    result_ids = fields.One2many(comodel_name='electronic.receipt.result.line', inverse_name='receipt_id',
                                 string=u'查询结果')

    @api.model
    def search_electronic_receipt_result(self, custNo, custName, slipId, slipNo, startDate, endDate):
        """查询电子回单信息"""
        # 检查输入的信息是否正确
        logging.info(u"开始查询客户'{}'的电子回单".format(custNo))
        if not custNo and not slipId and not custName and not slipNo:
            raise UserError(u"请输入客户编号或客户名称或电子回单编码或电子回单Id！")
        if not startDate and not endDate:
            raise UserError(u"请选择查询的开始和结束日期！")
        if not custNo:
            payment = self.env['interface.bank.payment'].sudo().search([('partner_id', '=', custName)])
            if payment:
                custNo = payment[0].partner_number
            else:
                raise UserError(u"客户：{}在付款单中不存在客户编号,不能进行查询！".format(custName))
        xml_str = cqt.package_electronic_return_inquiry({
            'offset': 0,
            'pageSize': 50,
            'custNo': custNo if custNo else '',
            'custName': custName if custName else '',
            'slipId': slipId if slipId else '',
            'slipNo': slipNo if slipNo else '',
            'startDate': startDate,
            'endDate': endDate,
        })
        logging.info(xml_str)
        # 获取财企通前置机地址
        service_url = self.env['ir.values'].get_default('interface.bank.settings', 'feg_add')
        # 发送报文到前置机
        result_xml = cqt.send_xml_to_cqtbankservice(xml_str, service_url)
        # 解析通用报文
        result = cqt.parsing_general_instruction_messages(result_xml)
        if isinstance(result, dict):
            if result['resultCode'] != '0000':
                msg = u"""执行失败！反馈代码: (%s),反馈消息: (%s)""" % (result['resultCode'], result['resultMsg'])
                logging.info(msg)
                raise UserError(msg)
        data = self.create_electronic_dict(result)
        self.env['interface.bank.electronic.receipt.result'].sudo().create(data)
        return {'state': True, 'msg': u'查询成功，请手动刷新并查看结果'}

    @api.model
    def get_state(self):
        return {'state': True}

    @api.multi
    def create_electronic_dict(self, res):
        """将传递的结果封装为data"""
        if isinstance(res, dict):
            e_data = {
                'custNo': self.custNo,
                'custName': self.custName,
                'slipId': self.slipId,
                'slipNo': self.slipNo,
                'startDate': self.startDate,
                'total': '1',
                'resultCode': res['resultCode'],
                'resultMsg': res['resultMsg'],
            }
            line_data = {
                'slipId': res['slipId'],
                'slipNo': res['slipNo'],
                'transNo': res['transNo'],
                'slipType': res['slipType'],
                'payUnitNo': res['payUnitNo'],
                'payUnitName': res['payUnitName'],
                'payAcntNo': res['payAcntNo'],
                'payAcntName': res['payAcntName'],
                'paySubAcntNo': res['paySubAcntNo'],
                'payBankName': res['payBankName'],
                'payBranchName': res['payBranchName'],
                'recUnitNo': res['recUnitNo'],
                'recUnitName': res['recUnitName'],
                'recAcntNo': res['recAcntNo'],
                'recAcntName': res['recAcntName'],
                'recBankName': res['recBankName'],
                'currencyCode': res['currencyCode'],
                'amount': res['amount'],
                'transDate': res['transDate'],
                'transTime': res['transTime'],
                'payUse': res['payUse'],
                'summary': res['summary'],
                'printTimes': res['printTimes'],
                'interest': res['interest'],
                'penalty': res['penalty'],
                'startDate': res['startDate'],
                'endDate': res['endDate'],
                'contNo': res['contNo'],
                'degProvideAcntNo': res['degProvideAcntNo'],
                'degIntAcntNo': res['degIntAcntNo'],
                'balance': res['balance'],
            }
            e_data['result_ids'] = line_data
            return e_data
        elif isinstance(res, list):
            e_data = {
                'custNo': self.custNo,
                'custName': self.custName,
                'slipId': self.slipId,
                'slipNo': self.slipNo,
                'startDate': self.startDate,
                'total': '1',
                # 'resultCode': res['resultCode'],
                # 'resultMsg': res['resultMsg'],
            }
            line_list = list()
            for line in res:
                line_data = {
                    'slipId': line['slipId'],
                    'slipNo': line['slipNo'],
                    'transNo': line['transNo'],
                    'slipType': line['slipType'],
                    'payUnitNo': line['payUnitNo'],
                    'payUnitName': line['payUnitName'],
                    'payAcntNo': line['payAcntNo'],
                    'payAcntName': line['payAcntName'],
                    'paySubAcntNo': line['paySubAcntNo'],
                    'payBankName': line['payBankName'],
                    'payBranchName': line['payBranchName'],
                    'recUnitNo': line['recUnitNo'],
                    'recUnitName': line['recUnitName'],
                    'recAcntNo': line['recAcntNo'],
                    'recAcntName': line['recAcntName'],
                    'recBankName': line['recBankName'],
                    'currencyCode': line['currencyCode'],
                    'amount': line['amount'],
                    'transDate': line['transDate'],
                    'transTime': line['transTime'],
                    'payUse': line['payUse'],
                    'summary': line['summary'],
                    'printTimes': line['printTimes'],
                    'interest': line['interest'],
                    'penalty': line['penalty'],
                    'startDate': line['startDate'],
                    'endDate': line['endDate'],
                    'contNo': line['contNo'],
                    'degProvideAcntNo': line['degProvideAcntNo'],
                    'degIntAcntNo': line['degIntAcntNo'],
                    'balance': line['balance'],
                }
                line_list.append((0, 0, line_data))
            e_data['result_ids'] = line_list
            return e_data


# 查询电子回单记录字表
class SearchElectronicReceiptResultLine(models.Model):
    _name = 'electronic.receipt.result.line'
    _description = u'查询电子回单记录字表'

    ELECTRONICTYPE = [
        ('01', u"交易"),
        ('02', u'费用'),
        ('03', u'结息'),
        ('04', u'贷款还款'),
        ('05', u'贷款还息'),
        ('06', u'交易冲正'),
        ('07', u'利息冲正'),
        ('08', u'贷款放款'),
    ]
    slipId = fields.Char(string=u'电子回单唯一标识')
    slipNo = fields.Char(string=u'电子回单号')
    transNo = fields.Char(string=u'业务流水')
    slipType = fields.Selection(string=u'回单类型', selection=ELECTRONICTYPE)
    payUnitNo = fields.Char(string=u'付款单位编号')
    payUnitName = fields.Char(string=u'付款单位名称')
    payAcntNo = fields.Char(string=u'付款账号')
    payAcntName = fields.Char(string=u'付款账户名')
    paySubAcntNo = fields.Char(string=u'付款子账户')
    payBankName = fields.Char(string=u'付款方银行')
    payBranchName = fields.Char(string=u'付款方开户行')
    recUnitNo = fields.Char(string=u'收款单位编号')
    recUnitName = fields.Char(string=u'收款单位名称')
    recAcntNo = fields.Char(string=u'收款方账号')
    recAcntName = fields.Char(string=u'收款方户名')
    recSubAcntNo = fields.Char(string=u'收款方子账号')
    recBankName = fields.Char(string=u'收款方银行名称')
    recBranchName = fields.Char(string=u'收款方开户行名称')
    currencyCode = fields.Char(string=u'币种')
    amount = fields.Char(string=u'金额')
    transDate = fields.Char(string=u'交易日期')
    transTime = fields.Char(string=u'交易时间')
    checkCode = fields.Char(string=u'验证码')
    payUse = fields.Char(string=u'付款用途')
    summary = fields.Char(string=u'摘要')
    printTimes = fields.Char(string=u'打印次数')
    interest = fields.Char(string=u'利息')
    penalty = fields.Char(string=u'罚息')
    startDate = fields.Char(string=u'开始时间')
    endDate = fields.Char(string=u'结束时间')
    contNo = fields.Char(string=u'合同号')
    iouNo = fields.Char(string=u'借据号')
    degProvideAcntNo = fields.Char(string=u'委贷放款账号')
    degIntAcntNo = fields.Char(string=u'收息账号')
    balance = fields.Char(string=u'余额')
    receipt_id = fields.Many2one(comodel_name='interface.bank.electronic.receipt.result', string=u'电子回单')


# 查询账户交易明细
class SerachAccountTransactionDetails(models.TransientModel):
    _name = 'search.account.transaction.details'
    _description = u"查询账户交易明细"

    SEARCHTYPE = [
        ('20003', u'内部账户交易明细'),
        ('20007', u'银行账户交易明细'),
        ('20017', u'头寸账户交易明细'),
    ]
    s_type = fields.Selection(string=u'查询类型', selection=SEARCHTYPE, default='20003', required=True)
    account_id = fields.Many2one(comodel_name='bank.public.accounts', string=u'查询账户', domain=[('btype', '!=', '01')])
    external_id = fields.Many2one(comodel_name='bank.external.accounts', string=u'银行账户')
    startDate = fields.Date(string=u'开始日期')
    endDate = fields.Date(string=u'结束日期')
    transId = fields.Char(string=u'交易ID')  # 内部账户交易时--开始和结束时间未填则笔录

    @api.multi
    def search_account_transaction_details(self):
        """开始查询账户交易明细"""
        # 获取财企通前置机地址
        service_url = self.env['ir.values'].get_default('interface.bank.settings', 'feg_add')
        xml_str = False
        result_xml = False
        result = False
        # 根据不同类型获取不同的xml
        if self.s_type == '20003':
            logging.info(u"开始查询内部账户交易明细")
            xml_str = cqt.package_query_internal_account_transaction_details_to_xml(self.account_id, self)
        elif self.s_type == '20007':
            logging.info(u"开始查询银行账户交易明细")
            xml_str = cqt.package_query_bank_account_transaction_details(self.external_id, self)
        elif self.s_type == '20017':
            logging.info(u"开始查询头寸账户交易明细")
            xml_str = cqt.package_query_position_account_transaction_details(self.account_id, self)
        logging.info(xml_str)
        # 发送报文到前置机
        if xml_str:
            result_xml = cqt.send_xml_to_cqtbankservice(xml_str, service_url)
        if result_xml:
            # 解析报文
            result_json = cqt.xml_to_json(result_xml)
            result_json = json.loads(result_json.strip())
            efmp = result_json['efmp']
            try:
                header = efmp['header']
            except KeyError:
                result = cqt.parsing_result_xml_result(efmp)
                msg = u"""查询发生错误，消息为：(%s)""" % result['resultMsg']
                logging.info(msg)
                raise UserError(msg)
            try:
                if header['resultCode'] != '0000':
                    msg = u"""执行失败！反馈代码: (%s),反馈消息: (%s)""" % (header['resultCode'], header['resultMsg'])
                    logging.info(msg)
                    raise UserError(msg)
            except KeyError:
                logging.info(header)
            result = cqt.parsing_result_xml_result(efmp)
            if isinstance(result, dict):
                try:
                    if result['resultCode'] != '0000':
                        msg = u"""执行失败！反馈代码: (%s),反馈消息: (%s)""" % (result['resultCode'], result['resultMsg'])
                        logging.debug(msg)
                        raise UserError(msg)
                except KeyError:
                    logging.debug(result)
            data = self.create_serach_account_transaction(result, self, header)
            transaction = self.env['bank.search.account.transaction'].sudo().create(data)
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'bank.search.account.transaction',
                'res_id': transaction.id,
            }

    @api.multi
    def create_serach_account_transaction(self, result, details, header):
        """根据选择的类型封装介意明细结果的dict
        :param result: result——json
        :param details: 查询交易明细对象
        :param header:解析结果中的header信息json
        :return dict: 根据details的类型封装不同的dict并返回
        """
        # 根据不同类型封装不同dict
        line_date = list()
        if details.s_type == '20003':
            if isinstance(result, dict):
                data = {
                    'transId': result['transId'],
                    'noteNo': result['noteNo'],
                    'custNo': result['custNo'],
                    'custName': result['custName'],
                    'acntNo': result['acntNo'],
                    'acntName': result['acntName'],
                    'transNo': result['transNo'],
                    'txnType': result['txnType'],
                    'txnDate': result['txnDate'],
                    'txnTime': result['txnTime'],
                    'oppAcntNo': result['oppAcntNo'],
                    'oppAcntName': result['oppAcntName'],
                    'oppBankName': result['oppBankName'],
                    'oppBranchName': result['oppBranchName'],
                    'currencyCode': result['currencyCode'],
                    'amount': result['amount'],
                    'summary': result['summary'],
                    'dcFlag': result['dcFlag'],
                    'balance': result['balance'],
                }
                line_date.append((0, 0, data))
            if isinstance(result, list):
                for res in result:
                    data = {
                        'transId': res['transId'],
                        'noteNo': res['noteNo'],
                        'custNo': res['custNo'],
                        'custName': res['custName'],
                        'acntNo': res['acntNo'],
                        'acntName': res['acntName'],
                        'transNo': res['transNo'],
                        'txnType': res['txnType'],
                        'txnDate': res['txnDate'],
                        'txnTime': res['txnTime'],
                        'oppAcntNo': res['oppAcntNo'],
                        'oppAcntName': res['oppAcntName'],
                        'oppBankName': res['oppBankName'],
                        'oppBranchName': res['oppBranchName'],
                        'currencyCode': res['currencyCode'],
                        'amount': res['amount'],
                        'summary': res['summary'],
                        'dcFlag': res['dcFlag'],
                        'balance': res['balance'],
                    }
                    line_date.append((0, 0, data))
        elif details.s_type == '20007':
            if isinstance(result, dict):
                data = {
                    'custNo': result['custNo'],
                    'custName': result['custName'],
                    'acntNo': result['bankAcntNo'],
                    'acntName': result['bankAcntName'],
                    'transNo': result['transNo'],
                    'txnType': result['txnType'],
                    'txnDate': result['txnDate'],
                    'txnTime': result['txnTime'],
                    'oppAcntNo': result['oppAcntNo'],
                    'oppAcntName': result['oppAcntName'],
                    'oppBankName': result['oppBankName'],
                    'oppBranchName': result['oppBranchName'],
                    'currencyCode': result['currencyCode'],
                    'amount': result['amount'],
                    'balance': result['balance'],
                    'payUse': result['payUse'],
                    'summary': result['summary'],
                    'postscript': result['postscript'],
                    'dcFlag': result['dcFlag'],
                    'uniqueFlag': result['uniqueFlag'],
                }
                line_date.append((0, 0, data))
            if isinstance(result, dict):
                for res in result:
                    data = {
                        'custNo': res['custNo'],
                        'custName': res['custName'],
                        'acntNo': res['bankAcntNo'],
                        'acntName': res['bankAcntName'],
                        'transNo': res['transNo'],
                        'txnType': res['txnType'],
                        'txnDate': res['txnDate'],
                        'txnTime': res['txnTime'],
                        'oppAcntNo': res['oppAcntNo'],
                        'oppAcntName': res['oppAcntName'],
                        'oppBankName': res['oppBankName'],
                        'oppBranchName': res['oppBranchName'],
                        'currencyCode': res['currencyCode'],
                        'amount': res['amount'],
                        'balance': res['balance'],
                        'payUse': res['payUse'],
                        'summary': res['summary'],
                        'postscript': res['postscript'],
                        'dcFlag': res['dcFlag'],
                        'uniqueFlag': res['uniqueFlag'],
                    }
                    line_date.append((0, 0, data))
        elif details.s_type == '20017':
            if isinstance(result, dict):
                data = {
                    'acntNo': result['bankAcntNo'],
                    'acntName': result['bankAcntName'],
                    'transNo': result['transNo'],
                    'txnType': result['txnType'],
                    'txnDate': result['txnDate'],
                    'txnTime': result['txnTime'],
                    'oppAcntNo': result['oppAcntNo'],
                    'oppAcntName': result['oppAcntName'],
                    'oppBankName': result['oppBankName'],
                    'oppBranchName': result['oppBranchName'],
                    'currencyCode': result['currencyCode'],
                    'amount': result['amount'],
                    'balance': result['balance'],
                    'payUse': result['payUse'],
                    'summary': result['summary'],
                    'postscript': result['postscript'],
                    'dcFlag': result['dcFlag'],
                    'uniqueFlag': result['uniqueFlag'],
                }
                line_date.append((0, 0, data))
            if isinstance(result, list):
                for res in result:
                    data = {
                        'acntNo': res['bankAcntNo'],
                        'acntName': res['bankAcntName'],
                        'transNo': res['transNo'],
                        'txnType': res['txnType'],
                        'txnDate': res['txnDate'],
                        'txnTime': res['txnTime'],
                        'oppAcntNo': res['oppAcntNo'],
                        'oppAcntName': res['oppAcntName'],
                        'oppBankName': res['oppBankName'],
                        'oppBranchName': res['oppBranchName'],
                        'currencyCode': res['currencyCode'],
                        'amount': res['amount'],
                        'balance': res['balance'],
                        'payUse': res['payUse'],
                        'summary': res['summary'],
                        'postscript': res['postscript'],
                        'dcFlag': res['dcFlag'],
                        'uniqueFlag': res['uniqueFlag'],
                    }
                    line_date.append((0, 0, data))
        return {
            's_type': details.s_type,
            'account_id': details.account_id.id,
            'createDate': header['createDate'],
            'offset': header['offset'],
            'pageSize': header['pageSize'],
            'total': header['total'],
            'packageId': header['packageId'],
            'resultCode': header['resultCode'],
            'resultMsg': header['resultMsg'],
            'result_ids': line_date,
        }


# 查询账户交易明细结果记录
class SerachAccountTransaction(models.Model):
    _name = 'bank.search.account.transaction'
    _description = u"查询账户交易明细结果记录"
    _rec_name = 'account_id'

    SEARCHTYPE = [
        ('20003', u'内部账户交易明细'),
        ('20007', u'银行账户交易明细'),
        ('20017', u'头寸账户交易明细'),
    ]
    s_type = fields.Selection(string=u'查询类型', selection=SEARCHTYPE, default='20003', required=True)
    account_id = fields.Many2one(comodel_name='bank.public.accounts', string=u'查询账户', domain=[('btype', '!=', '01')])
    createDate = fields.Char(string=u'查询日期')
    offset = fields.Char(string=u'起始记录数')
    pageSize = fields.Char(string=u'页记录数')
    total = fields.Char(string=u'记录总数')
    packageId = fields.Char(string=u'报文标识号')
    resultCode = fields.Char(string=u'结果码')
    resultMsg = fields.Char(string=u'结果信息')
    result_ids = fields.One2many(comodel_name='bank.search.account.transaction.result', inverse_name='transaction_id',
                                 string=u'查询结果')


# 交易明细结果记录行
class SerachAccountTransactionDetailsResultLine(models.Model):
    _name = 'bank.search.account.transaction.result'
    _description = u"交易明细结果记录行"

    transId = fields.Char(string=u'交易信息唯一编号')
    noteNo = fields.Char(string=u'客户单据号')
    custNo = fields.Char(string=u'客户编号')
    custName = fields.Char(string=u'客户名称')
    acntNo = fields.Char(string=u'账号')
    acntName = fields.Char(string=u'账户名称')

    transNo = fields.Char(string=u'交易流水')
    txnType = fields.Char(string=u'交易类型')
    txnDate = fields.Char(string=u'交易日期')
    txnTime = fields.Char(string=u'交易时间')
    oppAcntNo = fields.Char(string=u'对方账号')
    oppAcntName = fields.Char(string=u'对方户名')
    oppBankName = fields.Char(string=u'对方银行名称')
    oppBranchName = fields.Char(string=u'对方开户行名称')
    currencyCode = fields.Char(string=u'币种')
    amount = fields.Char(string=u'金额')
    summary = fields.Char(string=u'摘要')
    dcFlag = fields.Selection(string=u'借贷标识', selection=[('D', u'借'), ('C', u'贷'), ])
    balance = fields.Char(string=u'余额')
    uniqueFlag = fields.Char(string=u'唯一标识')
    payUse = fields.Char(string=u'付款用途')
    postscript = fields.Char(string=u'业务附言')
    transaction_id = fields.Many2one(comodel_name='bank.search.account.transaction', string=u'查询信息')


# 查询账户余额
class SerachAccountBalance(models.TransientModel):
    _name = 'search.bank.account.balance'
    _description = u"查询账户余额"

    @api.model
    def get_s_type(self):
        return [
            {'number': '20005', 'name': u'内部账户余额'},
            {'number': '20009', 'name': u'银行账户余额'},
            {'number': '20019', 'name': u'头寸账户余额'},
        ]

    @api.model
    def get_payment_account(self):
        return self.env['bank.public.accounts'].search_read([('btype', '!=', '01')], ['costomer_name'])

    @api.model
    def get_bank_account(self):
        return self.env['bank.external.accounts'].search_read([], ['name'])

    @api.model
    def search_account_bal_new(self, s_type, account_id, external_id):
        """开始查询账户余额"""
        accounts = self.env['bank.public.accounts'].sudo().search([('id', '=', account_id)])
        externals = self.env['bank.external.accounts'].sudo().search([('id', '=', external_id)])
        logging.info(u"开始查询账户余额")
        # 获取财企通前置机地址
        service_url = self.env['ir.values'].get_default('interface.bank.settings', 'feg_add')
        str_xml = False
        if s_type == '20005':
            logging.info(u"查询内部银行账户余额!")
            str_xml = cqt.package_query_internal_account_balance(accounts[0])
        elif s_type == '20009':
            logging.info(u"查询银行账户余额！")
            str_xml = cqt.package_search_bank_account_balance(externals[0])
        elif s_type == '20019':
            logging.info(u"查询头寸账户余额！")
            str_xml = cqt.package_search_money_supply_account_balance(accounts[0])
        logging.info(str_xml)
        result_xml = cqt.send_xml_to_cqtbankservice(str_xml, service_url)
        if result_xml:
            # 解析报文
            try:
                result_json = cqt.xml_to_json(result_xml)
            except ExpatError:
                raise UserError(u"解析结果错误！通常是由于前置机接口地址不正确而导致的！")
            result_json = json.loads(result_json.strip())
            efmp = result_json['efmp']
            header = False
            result = False
            try:
                header = efmp['header']
            except KeyError:
                result = cqt.parsing_result_xml_result(efmp)
                msg = u"""查询发生错误,消息为:(%s)""" % result['resultMsg']
                logging.info(msg)
                raise UserError(msg)
            try:
                if header['resultCode'] != '0000':
                    msg = u"""执行失败！反馈代码: (%s),反馈消息: (%s)""" % (header['resultCode'], header['resultMsg'])
                    logging.info(msg)
                    raise UserError(msg)
            except KeyError:
                logging.info(header)
            result = cqt.parsing_result_xml_result(efmp)
            if isinstance(result, dict):
                try:
                    if result['resultCode'] != '0000':
                        msg = u"""执行失败！反馈代码: (%s),反馈消息: (%s)""" % (result['resultCode'], result['resultMsg'])
                        logging.info(msg)
                        raise UserError(msg)
                except KeyError:
                    logging.debug(result)
            # 创建结果data
            data = self.get_result_data(result, header, s_type)
            return data['line_ids']

    @api.multi
    def get_result_data(self, result, header, s_type):
        """根据返回的结果封装成dict并返回
        :param result:xml转换的结果
        :param header: xml结果头部信息
        :param s_type: 查询表
        :return dict
        """
        result_list = list()
        if s_type == '20005':
            if isinstance(result, dict):
                data = {
                    'createDate': header['createDate'],
                    'createTime': header['createTime'],
                    'custNo': result['custNo'],
                    'custName': result['custName'],
                    'acntNo': result['acntNo'],
                    'acntName': result['acntName'],
                    'balance': result['balance'],
                    'availBalance': result['availBalance'],
                    'resultCode': result['resultCode'],
                    'resultMsg': result['resultMsg'],
                }
                result_list.append(data)
            elif isinstance(result, list):
                for res in result:
                    data = {
                        'createDate': header['createDate'],
                        'createTime': header['createTime'],
                        'custNo': res['custNo'],
                        'custName': res['custName'],
                        'acntNo': res['acntNo'],
                        'acntName': res['acntName'],
                        'balance': res['balance'],
                        'availBalance': res['availBalance'],
                        'resultCode': res['resultCode'],
                        'resultMsg': res['resultMsg'],
                    }
                    result_list.append(data)
        elif s_type == '20009':
            if isinstance(result, dict):
                data = {
                    'createDate': header['createDate'],
                    'createTime': header['createTime'],
                    'custNo': result['custNo'],
                    'custName': result['custName'],
                    'acntNo': result['bankAcntNo'],
                    'acntName': result['bankAcntName'],
                    'balance': result['balance'],
                    'availBalance': result['availBalance'],
                    'resultCode': result['resultCode'],
                    'resultMsg': result['resultMsg'],
                }
                result_list.append(data)
            elif isinstance(result, list):
                for res in result:
                    data = {
                        'createDate': header['createDate'],
                        'createTime': header['createTime'],
                        'custNo': res['custNo'],
                        'custName': res['custName'],
                        'acntNo': res['bankAcntNo'],
                        'acntName': res['bankAcntName'],
                        'balance': res['balance'],
                        'availBalance': res['availBalance'],
                        'resultCode': res['resultCode'],
                        'resultMsg': res['resultMsg'],
                    }
                    result_list.append(data)
        elif s_type == '20019':
            if isinstance(result, dict):
                data = {
                    'createDate': header['createDate'],
                    'createTime': header['createTime'],
                    'acntNo': result['bankAcntNo'],
                    'acntName': result['bankAcntName'],
                    'balance': result['balance'],
                    'availBalance': result['availBalance'],
                    'resultCode': result['resultCode'],
                    'resultMsg': result['resultMsg'],
                }
                result_list.append(data)
            elif isinstance(result, list):
                for res in result:
                    data = {
                        'createDate': header['createDate'],
                        'createTime': header['createTime'],
                        'acntNo': res['bankAcntNo'],
                        'acntName': res['bankAcntName'],
                        'balance': res['balance'],
                        'availBalance': res['availBalance'],
                        'resultCode': res['resultCode'],
                        'resultMsg': res['resultMsg'],
                    }
                    result_list.append(data)
        return {
            'packageId': header['packageId'],
            'line_ids': result_list,
        }


# 查询联行号CNAPS
class SearchBankNumber(models.TransientModel):
    _name = 'search.bank.number'
    _description = u"查询联行号CNAPS"

    bank_code = fields.Char(string=u'银行代码')

    @api.multi
    def search_bank_number(self):
        logging.info(u"开始查询联行号CNAPS")
        # 获取财企通前置机地址
        service_url = self.env['ir.values'].get_default('interface.bank.settings', 'feg_add')
        str_xml = cqt.package_query_the_company_number(self.bank_code)
        logging.info(str_xml)
        result_xml = cqt.send_xml_to_cqtbankservice(str_xml, service_url)
        # 解析报文
        result_json = cqt.xml_to_json(result_xml)
        result_json = json.loads(result_json.strip())
        efmp = result_json['efmp']
        result = False
        try:
            header = efmp['header']
        except KeyError:
            result = cqt.parsing_result_xml_result(efmp)
            msg = u"""查询发生错误,消息为:(%s)""" % result['resultMsg']
            logging.info(msg)
            raise UserError(msg)
        try:
            if header['resultCode'] != '0000':
                msg = u"""执行失败！反馈代码: (%s),反馈消息: (%s)""" % (header['resultCode'], header['resultMsg'])
                logging.info(msg)
                raise UserError(msg)
        except KeyError:
            logging.info(header)
        result = cqt.parsing_result_xml_result(efmp)
        if isinstance(result, dict):
            try:
                if result['resultCode'] != '0000':
                    msg = u"""执行失败！反馈代码: (%s),反馈消息: (%s)""" % (result['resultCode'], result['resultMsg'])
                    logging.info(msg)
                    raise UserError(msg)
            except KeyError:
                logging.debug(result)
        self.create_result(result)

    @api.multi
    def create_result(self, result):
        if isinstance(result, dict):
            data = {
                'bank_name': result['bankName'],
                'bank_code': result['bankCode'],
                'bank_type': result['bankType'],
                'cnapsCode': result['cnapsCode'],
                'swiftCode': result['swiftCode'],
                'provinceCode': result['provinceCode'],
                'provinceName': result['provinceName'],
                'cityCode': result['cityCode'],
                'cityName': result['cityName'],
                'lastModDate': result['lastModDate'],
                'lastModTime': result['lastModTime'],
                'strTimeStamp': result['strTimeStamp'],
                'deleteFlag': result['deleteFlag'],
            }
            self.env['search.bank.number.result'].sudo().create(data)
        elif isinstance(result, list):
            for res in result:
                data = {
                    'bank_name': res['bankName'],
                    'bank_code': res['bankCode'],
                    'bank_type': res['bankType'],
                    'cnapsCode': res['cnapsCode'],
                    'swiftCode': res['swiftCode'],
                    'provinceCode': res['provinceCode'],
                    'provinceName': res['provinceName'],
                    'cityCode': res['cityCode'],
                    'cityName': res['cityName'],
                    'lastModDate': res['lastModDate'],
                    'lastModTime': res['lastModTime'],
                    'strTimeStamp': res['strTimeStamp'],
                    'deleteFlag': res['deleteFlag'],
                }
                self.env['search.bank.number.result'].sudo().create(data)


# 查询联行号cnaps结果
class SearchBankResult(models.Model):
    _name = 'search.bank.number.result'
    _description = u"查询联行号cnaps结果"
    _rec_name = 'bank_name'

    bank_name = fields.Char(string=u'银行名称')
    bank_code = fields.Char(string=u'银行代码', required=True)
    bank_type = fields.Selection(string=u'银行类型', selection=[('0', u'总行'), ('1', u'分行/支行')])
    cnapsCode = fields.Char(string=u'CNAPS代码')
    swiftCode = fields.Char(string=u'SWIFT代码')
    provinceCode = fields.Char(string=u'省份代码')
    provinceName = fields.Char(string=u'省份名称')
    cityCode = fields.Char(string=u'城市代码')
    cityName = fields.Char(string=u'城市名称')
    lastModDate = fields.Char(string=u'最后更新日期')
    lastModTime = fields.Char(string=u'最后更新时间')
    strTimeStamp = fields.Char(string=u'上次更新的时间')
    deleteFlag = fields.Selection(string=u'删除标识', selection=[('0', u'正常'), ('1', u'删除')])


# 查询日资金计划
class SearchDailyFundPlan(models.TransientModel):
    _name = 'search.bank.daily.plan'
    _description = u"查询日资金计划"

    custNo = fields.Char(string=u'客户编号', required=True)
    planDate = fields.Date(string=u'计划日期', required=True)
    currencyCode = fields.Many2one(string=u'交易币种', comodel_name='bank.currency', required=True)

    @api.multi
    def search_daily_fund_plan(self):
        """查询日资金计划function"""
        logging.info(u"开始查询日资金计划")
        # 获取财企通前置机地址
        service_url = self.env['ir.values'].get_default('interface.bank.settings', 'feg_add')
        str_xml = cqt.package_daily_fund_plan_to_xml(self)
        logging.info(str_xml)
        result_xml = cqt.send_xml_to_cqtbankservice(str_xml, service_url)
        # 解析报文
        result_json = cqt.xml_to_json(result_xml)
        result_json = json.loads(result_json.strip())
        efmp = result_json['efmp']
        result = False
        try:
            header = efmp['header']
        except KeyError:
            result = cqt.parsing_result_xml_result(efmp)
            msg = u"""查询发生错误,消息为:(%s)""" % result['resultMsg']
            logging.info(msg)
            raise UserError(msg)
        try:
            if header['resultCode'] != '0000':
                msg = u"""执行失败！反馈代码: (%s),反馈消息: (%s)""" % (header['resultCode'], header['resultMsg'])
                logging.info(msg)
                raise UserError(msg)
        except KeyError:
            logging.info(header)
        result = cqt.parsing_result_xml_result(efmp)
        if isinstance(result, dict):
            try:
                if result['resultCode'] != '0000':
                    msg = u"""执行失败！反馈代码: (%s),反馈消息: (%s)""" % (result['resultCode'], result['resultMsg'])
                    logging.info(msg)
                    raise UserError(msg)
            except KeyError:
                logging.debug(result)
        self.create_search_result(result)

    @api.multi
    def create_search_result(self, result):
        """创建查询结果"""
        if isinstance(result, dict):
            bgtSet = result['bgtSet']
            bgt = bgtSet['bgt']
            line_list = list()
            if isinstance(bgt, dict):
                line_data = {
                    'itemNo': bgt['itemNo'],
                    'itemName': bgt['itemName'],
                    'occupyBudget': bgt['occupyBudget'],
                    'usedBudget': bgt['usedBudget'],
                    'availableBudget': bgt['availableBudget'],
                }
                line_list.append((0, 0, line_data))
            elif isinstance(bgt, list):
                for b in bgt:
                    line_data = {
                        'itemNo': b['itemNo'],
                        'itemName': b['itemName'],
                        'occupyBudget': b['occupyBudget'],
                        'usedBudget': b['usedBudget'],
                        'availableBudget': b['availableBudget'],
                    }
                    line_list.append((0, 0, line_data))
            self.env['search.daily.plan.result'].create({
                'custNo': result['custNo'],
                'planDate': result['planDate'],
                'currencyCode': result['currencyCode'],
                'occupyExpense': result['occupyExpense'],
                'usedExpense': result['usedExpense'],
                'availableExpense': result['availableExpense'],
                'resultCode': result['resultCode'],
                'resultMsg': result['resultMsg'],
                'line_ids': line_list,
            })
        elif isinstance(result, list):
            raise UserError(u"无处理返回值为list类型的方法！")


# 查询日资金计划结果
class BankDailyPlanResult(models.Model):
    _name = 'search.daily.plan.result'
    _description = u"查询日资金计划结果"
    _rec_name = 'custNo'

    custNo = fields.Char(string=u'客户编号')
    planDate = fields.Char(string=u'计划日期')
    currencyCode = fields.Many2one(string=u'交易币种', comodel_name='bank.currency', required=True)
    occupyExpense = fields.Float(string=u'已预占支出金额')
    usedExpense = fields.Float(string=u'已使用支出金额')
    availableExpense = fields.Float(string=u'可用支出金额')
    resultCode = fields.Char(string=u'结果码')
    resultMsg = fields.Char(string=u'结果信息')
    line_ids = fields.One2many(comodel_name='search.daily.plan.result.line', inverse_name='result_id', string=u'详细')


# 查询日资金计划结果子表
class BankDailyPlanResultLine(models.Model):
    _name = 'search.daily.plan.result.line'
    _description = u"查询日资金计划结果子表"
    _rec_name = 'itemNo'

    itemNo = fields.Char(string=u'项目编号')
    itemName = fields.Char(string=u'项目名称')
    occupyBudget = fields.Char(string=u'已预占金额')
    usedBudget = fields.Char(string=u'已使用金额')
    availableBudget = fields.Char(string=u'可用金额')
    result_id = fields.Many2one(comodel_name='search.daily.plan.result', string=u'日资金计划')
