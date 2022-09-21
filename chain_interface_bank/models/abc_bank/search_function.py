# -*- coding: utf-8 -*-
import datetime
import io
import json
import os
import xmltodict
from pyexpat import ExpatError
from xml.etree.ElementTree import tostring
from odoo import models, api, fields
import logging
from abc_functions import ABCFunctions as abc_function
from odoo.exceptions import UserError
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
_logger = logging.getLogger(__name__)


# 查询农行账户余额
class FindBankBal(models.TransientModel):
    _name = 'find.abc.account.bal'
    _description = u"查询农行账户余额"

    account_id = fields.Many2one(comodel_name='bank.public.accounts', string=u'查询账户', domain=[('btype', '!=', '00')],
                                 required=True)
    currency_id = fields.Many2one(comodel_name='bank.currency', string=u'交易币种')

    @api.model
    def start_find_account_bal(self, account_id, currency_id):
        """查询账户余额
        :param account_id 交易账户id
        :param currency_id 交易币种id
        """
        ACCDICT = {
            '0': u'基本存款账户',
            '1': u'辅助存款账户',
            '2': u'专用存款账户',
            '3': u'一般存款账户',
            '4': u'个人支票户',
            '5': u'可透支户',
            '6': u'临时存款账户',
            '7': u'注册验资临时存款户',
            '8': u'保证金户'
        }
        ACCSTS = {
            '0': u'正常',
            '1': u'销户',
            '2': u'异常',
            '9': u'全部',
        }
        logging.info(u"开始查询农业银行账户余额")
        # 获取付款的银行账户
        accounts = self.env['bank.public.accounts'].search([('id', '=', account_id)])
        currencys = self.env['bank.currency'].search([('id', '=', currency_id)])
        str_xml = abc_function.search_abc_bal(accounts, currencys[0])
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
            raise UserError(u"网络似乎出现了波动,导致系统接收的数据包不完整！请重试！")
        ap = result_json['ap']
        # 判断结果码是否为'0000'
        if ap['RespCode'] == '0000':
            corp = ap['Corp']
            data = ap['Acc']
            try:
                data['DbAccName'] = corp['DbAccName']
                data['costomer_number'] = accounts[0].costomer_number
                data['DbAccNo'] = accounts[0].payment_number
                data['AccType'] = ACCDICT[data['AccType']]
                data['AccSts'] = ACCSTS[data['AccSts']]
            except KeyError:
                return data
            return data
        else:
            raise UserError(ap['RespInfo'])

    @api.model
    def get_account(self):
        return self.env['bank.public.accounts'].search_read([('btype', '!=', '00')], ['costomer_name'])

    @api.model
    def get_currency(self):
        return self.env['bank.currency'].search_read([], ['name'])


# 查询账户交易明细
class SearchAbcBankTransactionDetails(models.Model):
    _description = u"查询账户交易明细"
    _rec_name = 'account_id'
    _name = 'find.abc.bank.tran.detail'

    start_date = fields.Date(string=u'开始日期', required=True)
    end_date = fields.Date(string=u'结束日期', required=True)
    account_id = fields.Many2one(comodel_name='bank.public.accounts', string=u'查询账户', domain=[('btype', '!=', '00')],
                                 required=True)
    currency_id = fields.Many2one(comodel_name='bank.currency', string=u'交易币种', required=True)
    line_ids = fields.One2many(comodel_name='find.abc.bank.tran.detail.line', inverse_name='detail_id', string=u'明细')

    @api.multi
    def search_bank_tran_detail(self):
        """查询银行账户交易明细
        """
        for res in self:
            res.line_ids = False
            logging.info(u"开始查询银行账户交易明细")
            # 获取付款的银行账户
            str_xml = abc_function.search_abc_tran_detail(res.account_id, res.start_date, res.end_date, res.currency_id)
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
                msg = u"由于网络原因,系统接收到的数据包不完整！导致无法识别查询结果,请重试!"
                raise UserError(msg)
            ap = result_json['ap']
            # 判断结果码是否为'0000'
            if ap['RespCode'] == '0000':
                Cmp = ap['Cmp']
                filename = Cmp['BatchFileName']
            else:
                msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
                raise UserError(msg)
            # 使用ftp下载文件
            abc_function.get_ftp_file(filename)
            # 读取文件内容
            res.line_ids = self.open_result_file(filename)

    @api.multi
    def open_result_file(self, file_name):
        """读取返回结果文件并创建到结果子表中
        :param file_name: 文件名
        :return list: 返回文件列表
        """
        result_file = io.open(file_name, 'r', encoding='gbk')
        file_list = result_file.readlines()
        line_list = list()
        for f in file_list:
            logging.info(f)
            txt_list = f.split('|')
            line_list.append({
                'Prov': txt_list[0],
                'AccNo': txt_list[1],
                'Cur': txt_list[2],
                'TrDate': txt_list[3],
                'TimeStab': txt_list[4],
                'TrJrn': txt_list[5],
                'TrType': txt_list[6],
                'TrBankNo': txt_list[7],
                'AccName': txt_list[8],
                'AmtIndex': txt_list[9],
                'OppProv': txt_list[10],
                'OppAccNo': txt_list[11],
                'OppCur': txt_list[12],
                'OppName': txt_list[13],
                'OppBkName': txt_list[14],
                'CshIndex': txt_list[15],
                'ErrDate': txt_list[16],
                'ErrVchNo': txt_list[17],
                'Amt': txt_list[18],
                'Bal': txt_list[19],
                'PreAmt': txt_list[20],
                'TotChg': txt_list[21],
                'VoucherType': txt_list[22],
                'VoucherProv': txt_list[23],
                'VoucherBat': txt_list[24],
                'VoucherNo': txt_list[25],
                'CustRef': txt_list[26],
                'TransCode': txt_list[27],
                'Teller': txt_list[28],
                'VchNo': txt_list[29],
                'Abs': txt_list[30],
                'PostScript': txt_list[31],
                'TrFrom': txt_list[32],
            })
        # 读取完成后删除文件
        os.remove(file_name)
        return line_list


class SearchAbcBankTransactionDetailsLine(models.Model):
    _name = 'find.abc.bank.tran.detail.line'
    _rec_name = 'detail_id'
    _description = u"查询账户交易明细"

    Prov = fields.Char(string=u'省市代码')
    AccNo = fields.Char(string=u'账号')
    Cur = fields.Char(string=u'货币码')
    TrDate = fields.Char(string=u'交易日期')
    TimeStab = fields.Char(string=u'交易时间')
    TrJrn = fields.Char(string=u'日志号')
    TrType = fields.Char(string=u'交易类型')
    TrBankNo = fields.Char(string=u'交易行号')
    AccName = fields.Char(string=u'户名')
    AmtIndex = fields.Char(string=u'发生额标志')
    OppProv = fields.Char(string=u'对方账号省市代码')
    OppAccNo = fields.Char(string=u'对方账号')
    OppCur = fields.Char(string=u'对方账号货币码')
    OppName = fields.Char(string=u'对方账号户名')
    OppBkName = fields.Char(string=u'对方账号开户')
    CshIndex = fields.Char(string=u'现转标志')
    ErrDate = fields.Char(string=u'错账日期')
    ErrVchNo = fields.Char(string=u'错账传票号')
    Amt = fields.Char(string=u'交易金额')
    Bal = fields.Char(string=u'账户余额')
    PreAmt = fields.Char(string=u'上笔余额')
    TotChg = fields.Char(string=u'手续费总额')
    VoucherType = fields.Char(string=u'凭证种类')
    VoucherProv = fields.Char(string=u'凭证省市代号')
    VoucherBat = fields.Char(string=u'凭证批次号')
    VoucherNo = fields.Char(string=u'凭证号')
    CustRef = fields.Char(string=u'客户参考号')
    TransCode = fields.Char(string=u'交易码')
    Teller = fields.Char(string=u'柜员号')
    VchNo = fields.Char(string=u'传票号')
    Abs = fields.Char(string=u'摘要')
    PostScript = fields.Char(string=u'附言')
    TrFrom = fields.Char(string=u'交易来源')
    detail_id = fields.Many2one(comodel_name='find.abc.bank.tran.detail', string=u'查询页', ondelete='cascade')


# TODO 暂无权限 查询农行账户账簿明细
class SearchBookDetails(models.Model):
    _name = 'interface.abc.book.detail'
    _description = u"查询农行账户账簿明细"
    _inherit = 'mail.thread'
    _rec_name = 'start_date'

    start_date = fields.Date(string=u'起始日期', required=True)
    end_date = fields.Date(string=u'终止日期', required=True)
    account_id = fields.Many2one(comodel_name='bank.public.accounts', string=u'查询账户', domain=[('btype', '!=', '00')],
                                 required=True)
    currency_id = fields.Many2one(comodel_name='bank.currency', string=u'交易币种')
    DbLogAccNo = fields.Char(string=u'起始多级账簿号')
    CrLogAccNo = fields.Char(string=u'终止多级账簿号')
    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 default=lambda self: self.env.user.company_id)
    line_ids = fields.One2many(comodel_name='interface.abc.book.detail.line', inverse_name='detail_id', string=u'明细行')

    @api.multi
    def search_abc_bank_detail(self):
        """查询农行账户账簿明细"""
        for res in self:
            str_xml = self.pagk_account_detail_xml(res)
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
                filename = Cmp['BatchFileName']
                msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
                res.message_post(body=msg, message_type='notification')
                # 使用ftp下载文件
                abc_function.get_ftp_file(filename)
                # 读取文件内容
                res.line_ids = self.write_result_file(filename)
            else:
                msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
                res.message_post(body=msg, message_type='notification')
                raise UserError(msg)

    @api.multi
    def pagk_account_detail_xml(self, res):
        """封装查询账簿明细xml CQRA14"""
        logging.info(u'封装查询明细xml')
        # 获取随机数用于流水号
        random = abc_function.get_random_str(25)
        # 企业操作员编号
        abc_operator_number = self.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
        # 认证码
        abc_auth_no = self.env['ir.values'].get_default('interface.bank.settings', 'abc_auth_no')
        # 数字签名
        abc_sign = self.env['ir.values'].get_default('interface.bank.settings', 'abc_sign')
        now_time = datetime.datetime.now()
        StartDate = datetime.datetime.strptime(res.start_date, '%Y-%m-%d')
        EndDate = datetime.datetime.strptime(res.end_date, '%Y-%m-%d')
        str_xml = {
            'CCTransCode': 'CQRA14',
            'ProductID': 'ICC',
            'ChannelType': 'ERP',
            'CorpNo': res.account_id.costomer_number,  # 企业技监局号码/客户号
            'OpNo': abc_operator_number,  # 企业操作员编号
            'AuthNo': abc_auth_no if abc_auth_no else '',  # 认证码
            'ReqSeqNo': random,  # 请求方流水号
            'ReqDate': now_time.strftime('%Y%m%d'),
            'ReqTime': now_time.strftime('%H%M%S'),
            'Sign': abc_sign if abc_sign else '',
            'Cmp': {
                'DbProv': res.account_id.abc_pc.code,  # 借方省市代码
                'DbAccNo': res.account_id.payment_number,  # 借方账号
                'DbCur': res.currency_id.number,  # 借方货币码
                'DbLogAccNo': res.DbLogAccNo if res.DbLogAccNo else '',  # 起始多级账簿号
                'CrLogAccNo': res.CrLogAccNo if res.CrLogAccNo else '',  # 终止多级账簿号
            },
            'Corp': {
                'StartDate': StartDate.strftime('%Y%m%d'),  # 起始日期
                'EndDate': EndDate.strftime('%Y%m%d'),  # 终止日期
            },
        }
        str_xml = abc_function.dict_to_xml('ap', str_xml)
        return tostring(str_xml)

    @api.multi
    def write_result_file(self, filename):
        """将接受到的文件写入到结果列表中
        :param filename: 文件名称
        :return list
        """
        result_file = io.open(filename, 'r', encoding='gbk')
        file_list = result_file.readlines()
        line_list = list()
        for f in file_list:
            logging.info(f)
            txt_list = f.split('|')
            line_list.append({
                'Prov': txt_list[0],
                'AccNo': txt_list[1],
                'LogAccNo': txt_list[2],
                'Cur': txt_list[3],
                'TrDate': txt_list[4],
                'TrJrn': txt_list[5],
                'TimeStab': txt_list[6],
                'AccName': txt_list[7],
                'LogAccName': txt_list[8],
                'TrType': txt_list[9],
                'TrBankNo': txt_list[10],
                'CreNo': txt_list[11],
                'AmtIndex': txt_list[12],
                'CshIndex': txt_list[13],
                'Amt': txt_list[14],
                'Bal': txt_list[15],
                'OvdAmt': txt_list[16],
                'VchType': txt_list[17],
                'TransCode': txt_list[18],
                'VchNo': txt_list[19],
                'OppProv': txt_list[20],
                'OppAccNo': txt_list[21],
                'OppCur': txt_list[22],
                'OppName': txt_list[23],
                'OppBank': txt_list[24],
                'ErrDate': txt_list[25],
                'ErrVch': txt_list[26],
                'Teller': txt_list[27],
                'Abs': txt_list[28],
                'Cmt': txt_list[29],
            })
        # 读取完成后删除文件
        os.remove(filename)
        return line_list


class SearchBookDetailsLine(models.Model):
    _name = 'interface.abc.book.detail.line'
    _description = u"查询农行账户账簿明细行"
    _rec_name = 'detail_id'

    detail_id = fields.Many2one(comodel_name='interface.abc.book.detail', string=u'账簿明细', ondelete='cascade')
    Prov = fields.Char(string=u'省市代码')
    AccNo = fields.Char(string=u'账号')
    LogAccNo = fields.Char(string=u'多级账簿号')
    Cur = fields.Char(string=u'货币码')
    TrDate = fields.Char(string=u'交易日期')
    TrJrn = fields.Char(string=u'日志号')
    TimeStab = fields.Char(string=u'交易时间')
    AccName = fields.Char(string=u'账号名称')
    LogAccName = fields.Char(string=u'账簿名称')
    TrType = fields.Char(string=u'交易类型')
    TrBankNo = fields.Char(string=u'交易行号')
    CreNo = fields.Char(string=u'传票号')
    AmtIndex = fields.Char(string=u'红蓝字标志')
    CshIndex = fields.Char(string=u'现转标志')
    Amt = fields.Char(string=u'交易金额')
    Bal = fields.Char(string=u'账户余额')
    OvdAmt = fields.Char(string=u'上笔余额')
    VchType = fields.Char(string=u'凭证种类')
    TransCode = fields.Char(string=u'交易码')
    VchNo = fields.Char(string=u'凭证号码')
    OppProv = fields.Char(string=u'对方省市代码')
    OppAccNo = fields.Char(string=u'对方账号')
    OppCur = fields.Char(string=u'对方币种')
    OppName = fields.Char(string=u'对方户名')
    OppBank = fields.Char(string=u'对方行名')
    ErrDate = fields.Char(string=u'错误日期')
    ErrVch = fields.Char(string=u'错误传票号')
    Teller = fields.Char(string=u'错误传票号')
    Abs = fields.Char(string=u'摘要')
    Cmt = fields.Char(string=u'备注')


# 查询异常交易
class AbnormalTransaction(models.TransientModel):
    _name = 'interface.abc.abnormal.transaction'
    _description = u"查询异常交易（CQRT04）"

    @api.model
    def get_payment(self):
        return self.env['interface.bank.payment'].search_read([('bank_type', '=', '01'), ('state', '=', '01')],
                                                              ['form_code'])

    @api.model
    def search_abc_transaction(self, account_id, currency_id, payment_code):
        """查询异常交易明细
        :param account_id 查询账户
        :param currency_id 交易币种
        :param payment_code 付款单编号
        """
        if not payment_code:
            raise UserError(u"请正确输入付款单编号!")
        logging.info(u"开始查询银行查询异常交易明细")
        # 获取付款银行
        bank = self.env['bank.public.accounts'].search([('id', '=', account_id)])
        # 获取币种
        currency = self.env['bank.currency'].search([('id', '=', currency_id)])
        # 获取付款单
        payment = self.env['interface.bank.payment'].search([('form_code', '=', payment_code)])
        if len(payment) != 1:
            raise UserError(u"单据编号不正确！请重新输入!")
        # xml
        str_xml = self.pack_search_abnormal_transaction_xml(bank, currency[0], payment)
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
            data = {
                'RespInfo': ap['RespInfo'],
                'DbAccNo': Cmp['DbAccNo'],
                'CmeSeqNo': Cmp['CmeSeqNo'],
                'RespPrvData': Cmp['RespPrvData'],
                'Postscript': Corp['Postscript'],
            }
            return data
        else:
            msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
            raise UserError(msg)

    @api.multi
    def pack_search_abnormal_transaction_xml(self, bank, currency, payment):
        """封装查询异常交易结果xml  (CQRT04)
        :param bank: 付款账户
        :param currency: 币种
        :param payment: 付款单
        :return string: 异常交易xml
        """
        # 获取随机数用于流水号
        random = abc_function.get_random_str(25)
        logging.info(u'封装查询异常交易结果xml--CQRT04')
        # 企业操作员编号
        abc_operator_number = self.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
        # 认证码
        abc_auth_no = self.env['ir.values'].get_default('interface.bank.settings', 'abc_auth_no')
        # 数字签名
        abc_sign = self.env['ir.values'].get_default('interface.bank.settings', 'abc_sign')
        now_time = datetime.datetime.now()
        str_xml = {
            'CCTransCode': 'CQRT04',
            'ProductID': 'ICC',
            'ChannelType': 'ERP',
            'CorpNo': bank.costomer_number,  # 企业技监局号码/客户号
            'OpNo': abc_operator_number,  # 企业操作员编号
            'AuthNo': abc_auth_no if abc_auth_no else '',  # 认证码
            'ReqSeqNo': random,  # 请求方流水号
            'ReqDate': now_time.strftime('%Y%m%d'),
            'ReqTime': now_time.strftime('%H%M%S'),
            'Sign': abc_sign if abc_sign else '',
            'Cmp': {
                'DbProv': bank.abc_pc.code if bank.abc_pc else '22',  # 借方省市代码
                'DbAccNo': bank.payment_number,  # 借方账号
                'DbCur': currency.number,  # 借方货币码
                'CmeSeqNo': payment.form_code,  # 客户端流水号(付款单编码)
            }
        }
        str_xml = abc_function.dict_to_xml('ap', str_xml)
        return tostring(str_xml)


# 查询联行行号
class SearchAbcBankNumber(models.TransientModel):
    _description = u"查询联行行号 (CQLT09)"
    _name = 'interface.abc.bank.number'

    @api.model
    def search_bank_number(self, account_id, bank_id, bank_name):
        """开始查询联行行号 CQLT09
        :param account_id 付款账户
        :param bank_id 银行行别
        :param bank_name 查询银行名称
        """
        logging.info(u"开始查询联行行号")
        accounts = self.env['bank.public.accounts'].search([('id', '=', account_id)])
        bank = self.env['interface.bank'].search([('id', '=', bank_id)])
        # 封装xml
        str_xml = self.pack_bank_number_xml(accounts[0], bank[0], bank_name)
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
            msg = u"由于网络原因,系统接收到的数据包不完整！导致无法识别查询结果,请重试!"
            raise UserError(msg)
        ap = result_json['ap']
        # 判断结果码是否为'0000'
        if ap['RespCode'] == '0000':
            Cmp = ap['Cmp']
            filename = Cmp['BatchFileName']
        else:
            msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
            raise UserError(msg)
        # 使用ftp下载文件
        abc_function.get_ftp_file(filename)
        # 读取文件内容
        return self.write_result_file(filename)

    @api.model
    def pack_bank_number_xml(self, accounts, bank, bank_name):
        """封装查询xml
        :param accounts: 付款账户
        :param bank: 银行行别
        :param bank_name: 查询银行名称
        """
        # 获取随机数用于流水号
        random = abc_function.get_random_str(25)
        # 企业操作员编号
        abc_operator_number = self.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
        # 认证码
        abc_auth_no = self.env['ir.values'].get_default('interface.bank.settings', 'abc_auth_no')
        # 数字签名
        abc_sign = self.env['ir.values'].get_default('interface.bank.settings', 'abc_sign')
        now_time = datetime.datetime.now()
        str_xml = {
            'CCTransCode': 'CQLT09',
            'ProductID': 'ICC',
            'ChannelType': 'ERP',
            'CorpNo': accounts.costomer_number,  # 企业技监局号码/客户号
            'OpNo': abc_operator_number if abc_operator_number else '',  # 企业操作员编号
            'AuthNo': abc_auth_no if abc_auth_no else '',  # 认证码
            'ReqSeqNo': random,  # 请求方流水号
            'ReqDate': now_time.strftime('%Y%m%d'),
            'ReqTime': now_time.strftime('%H%M%S'),
            'Sign': abc_sign if abc_sign else '',
            'Corp': {
                'CrBankName': bank_name,  # 贷方行名
                'CrBankType': bank.code,  # 他行行别
            }
        }
        str_xml = abc_function.dict_to_xml('ap', str_xml)
        return tostring(str_xml)

    @api.model
    def write_result_file(self, filename):
        """将接受到的文件写入到结果列表中
        :param filename: 文件名称
        :return list
        """
        result_file = io.open(filename, 'r', encoding='gbk')
        file_list = result_file.readlines()
        line_list = list()
        for f in file_list:
            logging.info(f)
            txt_list = f.split('|')
            line_list.append({
                'BankNo': txt_list[0],
                'BankName': txt_list[1],
            })
        # 读取完成后删除文件
        os.remove(filename)
        return line_list

    @api.model
    def get_abc_bank(self):
        return self.env['interface.bank'].search_read([], ['name'])


# 查询代收代付交易结果
class SearchAbcBankCollectionAndPayment(models.Model):
    _description = u'查询代收代付交易结果(CQRT02)'
    _name = 'interface.abc.collection.result'
    _rec_name = 'start_date'

    SEARCHTYPE = [
        ('1', u"代发工资"),
        ('2', u"费用报销"),
        ('3', u"批量代扣"),
    ]
    account_id = fields.Many2one(comodel_name='bank.public.accounts', string=u'内部账户', domain=[('btype', '!=', '00')],
                                 required=True)
    start_date = fields.Date(string=u'查询录入开始日期', required=True)
    end_date = fields.Date(string=u'查询录入终止日期', required=True)
    search_type = fields.Selection(string=u'查询业务类型', selection=SEARCHTYPE, default='1', required=True)
    line_ids = fields.One2many(comodel_name='interface.abc.collection.result.line', inverse_name='result_id',
                               string=u'结果')

    @api.multi
    def search_collection(self):
        """查询代收代付主函数 CQRT02"""
        logging.info(u"开始查询联行行号")
        for res in self:
            res.line_ids = False
            # 封装xml
            str_xml = self.pack_xml()
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
                msg = u"由于网络原因,系统接收到的数据包不完整！导致无法识别查询结果,请重试!"
                raise UserError(msg)
            ap = result_json['ap']
            # 判断结果码是否为'0000'
            if ap['RespCode'] == '0000':
                Cmp = ap['Cmp']
                filename = Cmp['BatchFileName']
            else:
                msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
                raise UserError(msg)
            # 使用ftp下载文件
            abc_function.get_ftp_file(filename)
            # 读取文件内容
            res.line_ids = self.write_result_file(filename)

    @api.multi
    def pack_xml(self):
        for res in self:
            # 获取随机数用于流水号
            random = abc_function.get_random_str(25)
            # 企业操作员编号
            abc_operator_number = self.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
            # 认证码
            abc_auth_no = self.env['ir.values'].get_default('interface.bank.settings', 'abc_auth_no')
            # 数字签名
            abc_sign = self.env['ir.values'].get_default('interface.bank.settings', 'abc_sign')
            now_time = datetime.datetime.now()
            StartDate = datetime.datetime.strptime(res.start_date, '%Y-%m-%d')
            EndDate = datetime.datetime.strptime(res.end_date, '%Y-%m-%d')
            str_xml = {
                'CCTransCode': 'CQRT02',
                'ProductID': 'ICC',
                'ChannelType': 'ERP',
                'CorpNo': res.account_id.costomer_number,  # 企业技监局号码/客户号
                'OpNo': abc_operator_number if abc_operator_number else '',  # 企业操作员编号
                'AuthNo': abc_auth_no if abc_auth_no else '',  # 认证码
                'ReqSeqNo': random,  # 请求方流水号
                'ReqDate': now_time.strftime('%Y%m%d'),
                'ReqTime': now_time.strftime('%H%M%S'),
                'Sign': abc_sign if abc_sign else '',
                'Corp': {
                    'StartDate': StartDate.strftime('%Y%m%d'),  # 开始日期
                    'EndDate': EndDate.strftime('%Y%m%d'),  # 结束日期
                    'PersonalFlag': res.search_type,  # 代收代付查询标志
                }
            }
            str_xml = abc_function.dict_to_xml('ap', str_xml)
            return tostring(str_xml)

    @api.multi
    def write_result_file(self, filename):
        """将接受到的文件写入到结果列表中
                :param filename: 文件名称
                :return list
                """
        result_file = io.open(filename, 'r', encoding='gbk')
        file_list = result_file.readlines()
        line_list = list()
        for f in file_list:
            logging.info(f)
            txt_list = f.split('|')
            line_list.append({
                'line1': txt_list[0],
                'line2': txt_list[1],
                'line3': txt_list[2],
                'line4': txt_list[3],
                'line5': txt_list[4],
                'line6': txt_list[5],
                'line7': txt_list[6],
                'line8': txt_list[7],
                'line9': txt_list[8],
                'line10': txt_list[9],
                'line11': txt_list[10],
                'line12': txt_list[11],
                'line13': txt_list[12],
                'line14': txt_list[13],
                'line15': txt_list[14],
                'line16': txt_list[15],
                'line17': txt_list[16],
                'line18': txt_list[17],
                'line19': txt_list[18],
                'line20': txt_list[19],
                'line21': txt_list[20],
            })
        # 读取完成后删除文件
        os.remove(filename)
        return line_list


class SearchAbcBankCollectionAndPaymentLine(models.Model):
    _description = u'代收代付交易结果'
    _name = 'interface.abc.collection.result.line'
    _rec_name = 'result_id'

    line1 = fields.Char(string=u'流水号')
    line2 = fields.Char(string=u'中间业务流水号')
    line3 = fields.Char(string=u'企业代码')
    line4 = fields.Char(string=u'行号')
    line5 = fields.Char(string=u'账号')
    line6 = fields.Char(string=u'申请总金额')
    line7 = fields.Char(string=u'申请总笔数')
    line8 = fields.Char(string=u'申请开始日期')
    line9 = fields.Char(string=u'申请结束日期')
    line10 = fields.Char(string=u'录入日期')
    line11 = fields.Char(string=u'处理状态')
    line12 = fields.Char(string=u'主机处理状态')
    line13 = fields.Char(string=u'成功总金额')
    line14 = fields.Char(string=u'成功总笔数')
    line15 = fields.Char(string=u'主机返回码')
    line16 = fields.Char(string=u'描述')
    line17 = fields.Selection(string=u'状态',
                              selection=[
                                  ('0', u'主机处理情况未知，需要继续查询'),
                                  ('1', u'中间业务处理失败'),
                                  ('2', u'交易成功'),
                                  ('8', u'账务已处理，但没有取到结果文件，请致电农行相关人员进行解决!'),
                                  ('9', u'查询失败'),
                              ])
    line18 = fields.Char(string=u'发送的文件名')
    line19 = fields.Char(string=u'返回处理结果文件')
    line20 = fields.Char(string=u'备注')
    line21 = fields.Selection(string=u'业务标志', selection=[('1', u'代发工资'), ('2', u'费用报销'), ('3', u'代理收款')])
    result_id = fields.Many2one(comodel_name='interface.abc.collection.result', string=u'代收代付交易', ondelete='cascade')


# TODO 暂无权限 查询账户支付限额
class SearchAbcBankPaymentLimit(models.TransientModel):
    _name = 'interface.abc.payment.limit'
    _description = u"查询账户支付限额"

    @api.model
    def search_payment_limit(self, account_id, currency_id):
        """查询账户支付限额
        :param account_id: 付款账户id
        :param currency_id: 币种id
        """
        logging.info(u"开始查询账户支付限额")
        logging.info(u"开始查询银行查询异常交易明细")
        # 获取付款银行
        bank = self.env['bank.public.accounts'].search([('id', '=', account_id)])
        # 获取币种
        currency = self.env['bank.currency'].search([('id', '=', currency_id)])
        # xml
        str_xml = self.pack_search_payment_limit_xml(bank, currency)
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
            return {
                'DbAccNo': Cmp['DbAccNo'],
                'AperPayLmt': Corp['AperPayLmt'],
                'AperCashLmt': Corp['AperCashLmt'],
                'EndDate': Corp['EndDate'],
                'StartDate': Corp['StartDate'],
                'MonPayLmt': Corp['MonPayLmt'],
                'MonCashLmt': Corp['MonCashLmt'],
                'DayPayLmt': Corp['DayPayLmt'],
                'DayCashLmt': Corp['DayCashLmt'],
                'SglPayLmt': Corp['SglPayLmt'],
                'SglCashLmt': Corp['SglCashLmt'],
                'DbAccName': Corp['DbAccName']
            }
        else:
            msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
            raise UserError(msg)

    @api.multi
    def pack_search_payment_limit_xml(self, bank, currency):
        """封装查询账户支付限额xml"""
        # 获取随机数用于流水号
        random = abc_function.get_random_str(25)
        logging.info(u'封装查询账户支付限额xml--CQRA03')
        # 企业操作员编号
        abc_operator_number = self.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
        # 认证码
        abc_auth_no = self.env['ir.values'].get_default('interface.bank.settings', 'abc_auth_no')
        # 数字签名
        abc_sign = self.env['ir.values'].get_default('interface.bank.settings', 'abc_sign')
        now_time = datetime.datetime.now()
        str_xml = {
            'CCTransCode': 'CQRA03',
            'ProductID': 'ICC',
            'ChannelType': 'ERP',
            'CorpNo': bank.costomer_number,  # 企业技监局号码/客户号
            'OpNo': abc_operator_number,  # 企业操作员编号
            'AuthNo': abc_auth_no if abc_auth_no else '',  # 认证码
            'ReqSeqNo': random,  # 请求方流水号
            'ReqDate': now_time.strftime('%Y%m%d'),
            'ReqTime': now_time.strftime('%H%M%S'),
            'Sign': abc_sign if abc_sign else '',
            'Cmp': {
                'DbProv': bank.abc_pc.code if bank.abc_pc else '22',  # 借方省市代码
                'DbAccNo': bank.payment_number,  # 借方账号
                'DbCur': currency.number,  # 借方货币码
            }
        }
        str_xml = abc_function.dict_to_xml('ap', str_xml)
        return tostring(str_xml)


# TODO 校验卡号、户名一致性
class SearchAbcBankAccountConsistent(models.TransientModel):
    _name = 'interface.abc.account.consistent'
    _description = u"校验卡号、户名一致性"

    @api.model
    def search_account_consistent(self, account_id, DbAccNo, DbAccName, Amt):
        """开始校验卡号户名是否一致
        :param account_id: 付款账户
        :param DbAccNo: 银行卡号
        :param DbAccName: 银行卡户名
        :param Amt: 金额
        """
        logging.info(u"开始校验卡号户名是否一致")
        if not DbAccNo:
            raise UserError(u"请正确填写银行卡号!")
        if not DbAccName:
            raise UserError(u"请正确填写银行卡户名!")
        Amt = '0' if not Amt else str(Amt)
        # xml
        # 获取付款银行
        bank = self.env['bank.public.accounts'].search([('id', '=', account_id)])
        str_xml = self.pack_account_consistent_xml(bank, DbAccNo.replace(' ', ''), DbAccName.replace(' ', ''), Amt)
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
            Acc = ap['Acc']
            Corp = ap['Corp']
            Pds = ap['Pds']
            return {
                'Name': Acc['Name'],
                'AccStatus': Acc['AccStatus'],
                'CustomNo': Corp['CustomNo'],
                'ProCod': Pds['ProCod'],
                'BrNo': Pds['BrNo'],
            }
        else:
            msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
            raise UserError(msg)

    @api.multi
    def pack_account_consistent_xml(self, bank, DbAccNo, DbAccName, Amt):
        """封装校验xml"""
        # 获取随机数用于流水号
        random = abc_function.get_random_str(25)
        logging.info(u'封装封装校验xml--CQRA22')
        # 企业操作员编号
        abc_operator_number = self.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
        # 认证码
        abc_auth_no = self.env['ir.values'].get_default('interface.bank.settings', 'abc_auth_no')
        # 数字签名
        abc_sign = self.env['ir.values'].get_default('interface.bank.settings', 'abc_sign')
        now_time = datetime.datetime.now()
        str_xml = {
            'CCTransCode': 'CQRA22',
            'ProductID': 'ICC',
            'ChannelType': 'ERP',
            'CorpNo': bank.costomer_number,  # 企业技监局号码/客户号
            'OpNo': abc_operator_number,  # 企业操作员编号
            'AuthNo': abc_auth_no if abc_auth_no else '',  # 认证码
            'ReqSeqNo': random,  # 请求方流水号
            'ReqDate': now_time.strftime('%Y%m%d'),
            'ReqTime': now_time.strftime('%H%M%S'),
            'Sign': abc_sign if abc_sign else '',
            'Amt': Amt,
            'Cmp': {
                'DbAccNo': DbAccNo,  # 借记卡卡号
            },
            'Corp': {
                'DbAccName': DbAccName,  # 借记卡户名
            }
        }
        str_xml = abc_function.dict_to_xml('ap', str_xml)
        return tostring(str_xml)


# 查询收费明细
class SearchChargeDetails(models.Model):
    _name = 'interface.abc.charge.detail'
    _description = u"查询收费明细"
    _rec_name = 'FeeCod'

    account_id = fields.Many2one(comodel_name='bank.public.accounts', string=u'内部账户', domain=[('btype', '!=', '00')],
                                 required=True)
    start_date = fields.Date(string=u'开始日期', required=True)
    end_date = fields.Date(string=u'终止日期', required=True)
    LastJrnNo = fields.Char(string=u'末笔日志号')
    FeeCod = fields.Many2one(comodel_name='interface.abc.charge.type', string=u'收费种类代码')
    ContFlag = fields.Selection(string=u'续查标志', selection=[('0', u'不续查'), ('1', u'续查'), ], default='0')
    RecInd = fields.Selection(string=u'收妥标志', selection=[('0', u'未收妥'), ('1', u'已收妥'), ], default='1')
    line_ids = fields.One2many(comodel_name='interface.abc.charge.detail.line', inverse_name='detail_id', string=u'结果')

    @api.multi
    def search_collection(self):
        """开始查询收费明细 CQRA11"""
        logging.info(u"开始查询收费明细")
        for res in self:
            res.line_ids = False
            # 封装xml
            str_xml = self.pack_xml()
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
                msg = u"由于网络原因,系统接收到的数据包不完整！导致无法识别查询结果,请重试!"
                raise UserError(msg)
            ap = result_json['ap']
            # 判断结果码是否为'0000'
            if ap['RespCode'] == '0000':
                Cmp = ap['Cmp']
                filename = Cmp['BatchFileName']
            else:
                msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
                raise UserError(msg)
            # 使用ftp下载文件
            abc_function.get_ftp_file(filename)
            # 读取文件内容
            res.line_ids = self.write_result_file(filename)

    @api.multi
    def pack_xml(self):
        for res in self:
            # 获取随机数用于流水号
            random = abc_function.get_random_str(25)
            # 企业操作员编号
            abc_operator_number = self.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
            # 认证码
            abc_auth_no = self.env['ir.values'].get_default('interface.bank.settings', 'abc_auth_no')
            # 数字签名
            abc_sign = self.env['ir.values'].get_default('interface.bank.settings', 'abc_sign')
            now_time = datetime.datetime.now()
            StartDate = datetime.datetime.strptime(res.start_date, '%Y-%m-%d')
            EndDate = datetime.datetime.strptime(res.end_date, '%Y-%m-%d')
            str_xml = {
                'CCTransCode': 'CQRA11',
                'ProductID': 'ICC',
                'ChannelType': 'ERP',
                'CorpNo': res.account_id.costomer_number,  # 企业技监局号码/客户号
                'OpNo': abc_operator_number if abc_operator_number else '',  # 企业操作员编号
                'AuthNo': abc_auth_no if abc_auth_no else '',  # 认证码
                'ReqSeqNo': random,  # 请求方流水号
                'ReqDate': now_time.strftime('%Y%m%d'),
                'ReqTime': now_time.strftime('%H%M%S'),
                'Sign': abc_sign if abc_sign else '',
                'Corp': {
                    'StartDate': StartDate.strftime('%Y%m%d'),  # 开始日期
                    'EndDate': EndDate.strftime('%Y%m%d'),  # 结束日期
                    'LastJrnNo': res.LastJrnNo if res.LastJrnNo else '',  # 末笔日志号
                },
                'Cmp': {
                    'DbAccNo': res.account_id.payment_number,  # 账号
                    'DbProv': res.account_id.abc_pc.code if res.account_id.abc_pc else '22',  # 省市代码
                    'DbCur': '01',  # 货币码
                    'FeeCod': res.FeeCod.code if res.FeeCod else '',  # 收费种类
                    'ContFlag': res.ContFlag,  # 续查标志
                    'RecInd': res.RecInd,  # 收妥标志
                }
            }
            str_xml = abc_function.dict_to_xml('ap', str_xml)
            return tostring(str_xml)

    @api.multi
    def write_result_file(self, filename):
        """将接受到的文件写入到结果列表中
                :param filename: 文件名称
                :return list
                """
        result_file = io.open(filename, 'r', encoding='gbk')
        file_list = result_file.readlines()
        line_list = list()
        for f in file_list:
            logging.info(f)
            txt_list = f.split('|')
            line_list.append({
                'line1': txt_list[0],
                'line2': txt_list[1],
                'line3': txt_list[2],
                'line4': txt_list[3],
                'line5': txt_list[4],
                'line6': txt_list[5],
                'line7': txt_list[6],
                'line8': txt_list[7],
                'line9': txt_list[8],
                'line10': txt_list[9],
                'line11': txt_list[10],
                'line12': txt_list[11],
                'line13': txt_list[12],
                'line14': txt_list[13],
                'line15': txt_list[14],
                'line16': txt_list[15],
                'line17': txt_list[16],
                'line18': txt_list[17],
                'line19': txt_list[18],
                'line20': txt_list[19],
                'line21': txt_list[20],
                'line22': txt_list[21],
            })
        # 读取完成后删除文件
        os.remove(filename)
        return line_list


class SearchChargeDetailsLine(models.Model):
    _name = 'interface.abc.charge.detail.line'
    _description = u"收费明细列表"
    _rec_name = 'detail_id'

    line1 = fields.Char(string=u'省市代码')
    line2 = fields.Char(string=u'账户')
    line3 = fields.Char(string=u'货币码')
    line4 = fields.Char(string=u'收费种类代码')
    line5 = fields.Char(string=u'收费种类名称')
    line6 = fields.Char(string=u'收费账户户名')
    line7 = fields.Char(string=u'登记日期')
    line8 = fields.Char(string=u'登记日志号')
    line9 = fields.Char(string=u'收妥日期')
    line10 = fields.Char(string=u'收费周期')
    line11 = fields.Char(string=u'收费基数')
    line12 = fields.Char(string=u'费率')
    line13 = fields.Char(string=u'交易量')
    line14 = fields.Char(string=u'金额')
    line15 = fields.Char(string=u'应收金额')
    line16 = fields.Char(string=u'已收金额')
    line17 = fields.Selection(string=u'收妥标志', selection=[('1', u'未收妥'), ('2', u'已收妥'), ], default='1')
    line18 = fields.Char(string=u'交易码')
    line19 = fields.Char(string=u'柜员号')
    line20 = fields.Char(string=u'传票号')
    line21 = fields.Char(string=u'摘要')
    line22 = fields.Char(string=u'交易来源')
    detail_id = fields.Many2one(comodel_name='interface.abc.charge.detail', string=u'收费明细', ondelete='cascade')


# 查询工资处理结果(新版)
class SearchAbcWagesResult(models.TransientModel):
    _description = u"查询工资处理结果"
    _name = 'interface.abc.search.wages.result'

    @api.model
    def search_wages_result(self, account_id, form_code):
        """根据代发工资交易流水号进行查询
        :param account_id: 交易账户
        :param form_code: 代发工资交易流水
        """
        if not form_code:
            raise UserError(u"要查询的流水号不能为空！")
        logging.info(u"要查询的代发工资流水号为：".format(form_code))
        # 获取付款银行
        bank = self.env['bank.public.accounts'].search([('id', '=', account_id)])
        str_xml = self.pack_xml(bank, form_code)
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
            # 判断是否有文件
            if ap['FileFlag'] == '1':
                Cmp = ap['Cmp']
                filename = Cmp['BatchFileName']
                # 使用ftp下载文件
                abc_function.get_ftp_file(filename)
                # 读取并返回文件内容
                return self.read_file_info(filename)
        else:
            msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
            raise UserError(msg)

    @api.multi
    def pack_xml(self, bank, form_code):
        # 获取随机数用于流水号
        random = abc_function.get_random_str(25)
        logging.info(u'查询工资处理结果xml--CQLT73')
        # 企业操作员编号
        abc_operator_number = self.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
        # 认证码
        abc_auth_no = self.env['ir.values'].get_default('interface.bank.settings', 'abc_auth_no')
        # 数字签名
        abc_sign = self.env['ir.values'].get_default('interface.bank.settings', 'abc_sign')
        now_time = datetime.datetime.now()
        str_xml = {
            'CCTransCode': 'CQLT73',
            'ProductID': 'ICC',
            'ChannelType': 'ERP',
            'CorpNo': bank.costomer_number,  # 企业技监局号码/客户号
            'OpNo': abc_operator_number,  # 企业操作员编号
            'AuthNo': abc_auth_no if abc_auth_no else '',  # 认证码
            'ReqSeqNo': random,  # 请求方流水号
            'ReqDate': now_time.strftime('%Y%m%d'),
            'ReqTime': now_time.strftime('%H%M%S'),
            'Sign': abc_sign if abc_sign else '',
            'Corp': {
                'CustomNo': form_code,  # 原代发工资交易的请求号
            }
        }
        str_xml = abc_function.dict_to_xml('ap', str_xml)
        return tostring(str_xml)

    @api.multi
    def read_file_info(self, filename):
        """将接受到的文件写入到结果列表中
        :param filename: 文件名称
        :return list
        """
        result_file = io.open(filename, 'r', encoding='gbk')
        file_list = result_file.readlines()
        line_list = list()
        line_state = {'E': u"处理失败", 'P': u"尚未处理", 'S': u"处理成功"}
        for f in file_list:
            logging.info(f)
            txt_list = f.split('|')
            line_list.append({
                'line1': txt_list[0],
                'line2': line_state[txt_list[1]],
                'line3': txt_list[2],
                'line4': txt_list[3],
                'line5': txt_list[4],
                'line6': txt_list[5],
                'line7': txt_list[6],
            })
        # 读取完成后删除文件
        os.remove(filename)
        return line_list


# 查询代发工资文件明细
class SearchAbcWagesFileDetail(models.TransientModel):
    _description = u"查询代发工资文件明细"
    _name = 'interface.abc.search.file.detail'

    @api.model
    def search_file_detail(self, account_id, form_code):
        """查询代发工资文件明细
        :param account_id: 交易账户
        :param form_code: 代发工资交易流水
        """
        if not form_code:
            raise UserError(u"要查询的流水号不能为空！")
        logging.info(u"查询代发工资文件明细流水号为：".format(form_code))
        # 获取付款银行
        bank = self.env['bank.public.accounts'].search([('id', '=', account_id)])
        str_xml = self.pack_xml(bank, form_code)
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
            # 判断是否有文件
            if ap['FileFlag'] == '1':
                Cmp = ap['Cmp']
                filename = Cmp['BatchFileName']
                # 使用ftp下载文件
                abc_function.get_ftp_file(filename)
                # 读取并返回文件内容
                return self.read_file_info(filename)
        else:
            msg = "{};{}".format(ap['RespInfo'], ap['RxtInfo'] if ap['RxtInfo'] else '')
            raise UserError(msg)

    @api.multi
    def pack_xml(self, bank, form_code):
        # 获取随机数用于流水号
        random = abc_function.get_random_str(25)
        logging.info(u'查询代发工资文件明细--CQLO07')
        # 企业操作员编号
        abc_operator_number = self.env['ir.values'].get_default('interface.bank.settings', 'abc_operator_number')
        # 认证码
        abc_auth_no = self.env['ir.values'].get_default('interface.bank.settings', 'abc_auth_no')
        # 数字签名
        abc_sign = self.env['ir.values'].get_default('interface.bank.settings', 'abc_sign')
        now_time = datetime.datetime.now()
        str_xml = {
            'CCTransCode': 'CQLO07',
            'ProductID': 'ICC',
            'ChannelType': 'ERP',
            'CorpNo': bank.costomer_number,  # 企业技监局号码/客户号
            'OpNo': abc_operator_number,  # 企业操作员编号
            'AuthNo': abc_auth_no if abc_auth_no else '',  # 认证码
            'ReqSeqNo': random,  # 请求方流水号
            'ReqDate': now_time.strftime('%Y%m%d'),
            'ReqTime': now_time.strftime('%H%M%S'),
            'Sign': abc_sign if abc_sign else '',
            'Cme': {
                'SerialNo': form_code,  # 系统流水号
            }
        }
        str_xml = abc_function.dict_to_xml('ap', str_xml)
        return tostring(str_xml)

    @api.multi
    def read_file_info(self, filename):
        """将接受到的文件写入到结果列表中
        :param filename: 文件名称
        :return list
        """
        result_file = io.open(filename, 'r', encoding='gbk')
        file_list = result_file.readlines()
        line_list = list()
        line_state = {'E': u"处理失败", 'P': u"尚未处理", 'S': u"处理成功"}
        for f in file_list:
            logging.info(f)
            txt_list = f.split('|')
            line_list.append({
                'line1': txt_list[0],
                'line2': line_state[txt_list[1]],
                'line3': txt_list[2],
                'line4': txt_list[3],
                'line5': txt_list[4],
                'line6': txt_list[5],
                'line7': txt_list[6],
            })
        # 读取完成后删除文件
        # os.remove(filename)
        return line_list
