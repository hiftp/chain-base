# -*- coding: utf-8 -*-
import datetime
import xml.dom.minidom
import logging
import json
import xmltodict
import requests
from bs4 import BeautifulSoup
from requests import ConnectionError

from odoo.exceptions import UserError
from odoo.http import request
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class CqtFunction(classmethod):
    """本class是为财企通提供封装成xml字符串的所有functions"""

    @classmethod
    def send_xml_to_cqtbankservice(cls, efmp_xml, service_url):
        """将封装的xml字符串和前置机地址调用财企通外部接口发送付款信息
        :param efmp_xml: 付款信息的xml字符串
        :param service_url: 财企通前置机地址url
        :return result_xml: 银行返回结果xml
        """
        res = False
        try:
            res = requests.post(url=service_url, data=efmp_xml, timeout=20)
        except ConnectionError:
            raise UserError(u"网络连接失败，请重试！")
        logging.info(res.content)
        return res.content

    @classmethod
    def xml_to_dict(cls, xml_data):
        """
        xml转换为字典
        :param xml_data: xml字符串
        :return: data: 转换为data字典
        """
        soup = BeautifulSoup(xml_data, features='xml')
        xml = soup.find('efmp')
        if not xml:
            return {}
        # 将 XML 数据转化为 Dict
        return dict([(item.name, item.text) for item in xml.find_all()])

    @classmethod
    def xml_to_json(cls, xmlstr):
        """将字符串xml转换为json
        :param xmlstr: xml字符串
        """
        return json.dumps(xmltodict.parse(xmlstr), indent=1)

    @classmethod
    def parsing_general_instruction_messages(cls, result_xml):
        """解析通用响应报文
        :param result_xml: 结果xml
        :return dict: 返回结果字典
        """
        result_json = cls.xml_to_json(result_xml)
        result_json = json.loads(result_json.strip())
        efmp = result_json['efmp']
        body = efmp['body']
        result_set = body['resultSet']
        result = result_set['result']
        return result

    @classmethod
    def parsing_result_xml_result(cls, efmp):
        """解析json（efmp）里面的result结果并返回
        :param efmp: 结果json对象
        :return dict
        """
        try:
            body = efmp['body']
            result_set = body['resultSet']
            result = result_set['result']
            return result
        except KeyError:
            mes = u"财企通系统未返回任何数据,详细信息请查看log输出日志!"
            logging.info(mes)
            raise UserError(mes)

    @classmethod
    def package_payment_to_xml(cls, payment, public_account):
        """将付款信息封装成类型为'付款'的xml并返回(10001)
        :param payment: 付款单
        :param public_account: 付款确认向导
        :return string: 付款xml字符串
        """
        csystem_code = request.env['ir.values'].get_default('interface.bank.settings', 'p_csystem_code')
        csystem_name = request.env['ir.values'].get_default('interface.bank.settings', 'p_csystem_name')
        now_time = datetime.datetime.now()

        doc = xml.dom.minidom.Document()
        # 根元素以及属性
        efmp = doc.createElement('efmp')
        efmp.setAttribute('standard', 'FEG')
        efmp.setAttribute('type', '10001')
        efmp.setAttribute('version', '1.0')
        # -----头部信息----
        header = doc.createElement('header')
        appCode = doc.createElement('appCode')
        appCode.appendChild(doc.createTextNode(csystem_code))  # 接入系统代码
        appName = doc.createElement('appName')
        appName.appendChild(doc.createTextNode(csystem_name))  # 接入系统名称
        packageId = doc.createElement('packageId')
        packageId.appendChild(doc.createTextNode(payment.form_code))  # 报文标识号
        createDate = doc.createElement('createDate')
        createDate.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d')))  # 报文日期（yyyyMMdd）
        createTime = doc.createElement('createTime')
        createTime.appendChild(doc.createTextNode(now_time.strftime('%H%M%S')))  # 提交时间（HHmmss）
        header.appendChild(appCode)
        header.appendChild(appName)
        header.appendChild(packageId)
        header.appendChild(createDate)
        header.appendChild(createTime)
        efmp.appendChild(header)
        # ----消息体信息----
        body = doc.createElement('body')
        paramSet = doc.createElement('paramSet')

        # -----每笔付款信息----
        param = doc.createElement('param')

        requestId = doc.createElement('requestId')
        requestId.appendChild(doc.createTextNode(payment.form_code))  # 单笔唯一标识
        param.appendChild(requestId)
        noteNo = doc.createElement('noteNo')
        noteNo.appendChild(doc.createTextNode(payment.form_code))  # 客户单据号（非必填）
        param.appendChild(noteNo)
        transNo = doc.createElement('transNo')
        transNo.appendChild(doc.createTextNode(payment.form_code))  # 业务流水号（非必填）
        param.appendChild(transNo)
        payUnitNo = doc.createElement('payUnitNo')
        payUnitNo.appendChild(doc.createTextNode(public_account.costomer_number))  # 付款方客户编号
        param.appendChild(payUnitNo)
        payUnitName = doc.createElement('payUnitName')
        payUnitName.appendChild(doc.createTextNode(public_account.costomer_name))  # 付款方客户名称
        param.appendChild(payUnitName)
        payAcntNo = doc.createElement('payAcntNo')
        payAcntNo.appendChild(doc.createTextNode(public_account.payment_number))  # 付款方账号
        param.appendChild(payAcntNo)
        payAcntName = doc.createElement('payAcntName')
        payAcntName.appendChild(doc.createTextNode(public_account.payment_username))  # 付款方户名
        param.appendChild(payAcntName)
        recUnitNo = doc.createElement('recUnitNo')
        recUnitNo.appendChild(doc.createTextNode(payment.form_code))  # 收款客户编号（非必填"
        param.appendChild(recUnitNo)
        recUnitName = doc.createElement('recUnitName')
        recUnitName.appendChild(doc.createTextNode(payment.partner_id))  # 收款客户名称（非必填
        param.appendChild(recUnitName)
        recAcntNo = doc.createElement('recAcntNo')
        recAcntNo.appendChild(doc.createTextNode(payment.partner_bank_number))  # 收款方账号
        param.appendChild(recAcntNo)
        recAcntName = doc.createElement('recAcntName')
        recAcntName.appendChild(doc.createTextNode(payment.partner_id))  # 收款方户名
        param.appendChild(recAcntName)
        # 判断是否对外转账
        if payment.payee_identi == '01':
            recBankCode = doc.createElement('recBankCode')
            recBankCode.appendChild(doc.createTextNode(payment.payee_bank_code))  # 收款方银行代码（对外时必填）
            param.appendChild(recBankCode)
            recBankName = doc.createElement('recBankName')
            recBankName.appendChild(doc.createTextNode(payment.payee_bank))  # 收款银行名称（对外时必填）
            param.appendChild(recBankName)
            recBranchCode = doc.createElement('recBranchCode')
            recBranchCode.appendChild(doc.createTextNode(payment.payee_opening_bank_code))  # 收款方开户行（对外时必填）
            param.appendChild(recBranchCode)
            recBranchName = doc.createElement('recBranchName')
            recBranchName.appendChild(doc.createTextNode(payment.payee_opening_bank))  # 收款方开户行名称（对外时必填）
            param.appendChild(recBranchName)
            recProvinceCode = doc.createElement('recProvinceCode')
            recProvinceCode.appendChild(doc.createTextNode(payment.payee_opening_province_code))  # 收款方省份代码（非必填）
            param.appendChild(recProvinceCode)
            recProvinceName = doc.createElement('recProvinceName')
            recProvinceName.appendChild(doc.createTextNode(payment.payee_opening_province))  # 收款方省份名称（非必填）
            param.appendChild(recProvinceName)
            recCityCode = doc.createElement('recCityCode')
            recCityCode.appendChild(doc.createTextNode(payment.payee_opening_city_code))  # 收款方城市代码（非必填）
            param.appendChild(recCityCode)
            recCityName = doc.createElement('recCityName')
            recCityName.appendChild(doc.createTextNode(payment.payee_opening_city))  # 收款方城市名称（非必填）
            param.appendChild(recCityName)
        recLinkman = doc.createElement('recLinkman')
        if payment.partner_contact:
            recLinkman.appendChild(doc.createTextNode(payment.partner_contact))  # 收款方联系人（非必填）
        param.appendChild(recLinkman)
        recLinkPhone = doc.createElement('recLinkPhone')
        if payment.partner_contact_phone:
            recLinkPhone.appendChild(doc.createTextNode(payment.partner_contact_phone))  # 收款方联系电话（非必填）
        param.appendChild(recLinkPhone)
        recLinkAddress = doc.createElement('recLinkAddress')
        if payment.partner_contact_add:
            recLinkAddress.appendChild(doc.createTextNode(payment.partner_contact_add))  # 收款方联系地址（非必填）
        param.appendChild(recLinkAddress)
        recRemark = doc.createElement('recRemark')
        if payment.pay_summary:
            recRemark.appendChild(doc.createTextNode(payment.pay_summary))  # 收款方备注（非必填）
        param.appendChild(recRemark)
        currencyCode = doc.createElement('currencyCode')
        currencyCode.appendChild(doc.createTextNode(payment.currency_type.code))  # 币种
        param.appendChild(currencyCode)
        amount = doc.createElement('amount')
        amount.appendChild(doc.createTextNode(str(payment.pay_money)))  # 付款金额
        param.appendChild(amount)
        txnDate = doc.createElement('txnDate')
        txnDate.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d')))  # 交易日期YYYYmmdd
        param.appendChild(txnDate)
        payUse = doc.createElement('payUse')
        if payment.pay_use:
            payUse.appendChild(doc.createTextNode(payment.pay_use))  # 付款用途 非必填
        param.appendChild(payUse)
        payMode = doc.createElement('payMode')
        if payment.payment_model:
            payMode.appendChild(doc.createTextNode(payment.payment_model))  # 付款模式（非必填）
        param.appendChild(payMode)
        summary = doc.createElement('summary')
        if payment.pay_summary:
            summary.appendChild(doc.createTextNode(payment.pay_summary))  # 付款摘要（非必填）
        param.appendChild(summary)
        corpFlag = doc.createElement('corpFlag')
        corpFlag.appendChild(doc.createTextNode(payment.public_signs))  # 公私标识
        param.appendChild(corpFlag)
        recFlag = doc.createElement('recFlag')
        recFlag.appendChild(doc.createTextNode(payment.payee_identi))  # 收款方标识
        param.appendChild(recFlag)
        # 加入每笔付款
        paramSet.appendChild(param)
        # 加入到body
        body.appendChild(paramSet)
        # 添加到跟元素中
        efmp.appendChild(body)
        doc.appendChild(efmp)
        return doc.toprettyxml(encoding='utf-8')

    @classmethod
    def package_agent_payment_to_xml(cls, payment, public_account):
        """根据付款单和确认向导封装封装一个用于财企通代理付款的xml字符串(70003)
        :param payment: 付款单
        :param public_account: 付款确认向导
        :return string: 付款xml字符串
        """
        csystem_code = request.env['ir.values'].get_default('interface.bank.settings', 'p_csystem_code')
        csystem_name = request.env['ir.values'].get_default('interface.bank.settings', 'p_csystem_name')
        now_time = datetime.datetime.now()

        doc = xml.dom.minidom.Document()
        # 根元素以及属性
        efmp = doc.createElement('efmp')
        efmp.setAttribute('standard', 'FEG')
        efmp.setAttribute('type', '70003')
        efmp.setAttribute('version', '1.0')
        # -----头部信息----
        header = doc.createElement('header')
        appCode = doc.createElement('appCode')
        appCode.appendChild(doc.createTextNode(csystem_code))  # 接入系统代码
        appName = doc.createElement('appName')
        appName.appendChild(doc.createTextNode(csystem_name))  # 接入系统名称
        packageId = doc.createElement('packageId')
        packageId.appendChild(doc.createTextNode(payment.form_code))  # 报文标识号
        createDate = doc.createElement('createDate')
        createDate.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d')))  # 报文日期（yyyyMMdd）
        createTime = doc.createElement('createTime')
        createTime.appendChild(doc.createTextNode(now_time.strftime('%H%M%S')))  # 提交时间（HHmmss）
        header.appendChild(appCode)
        header.appendChild(appName)
        header.appendChild(packageId)
        header.appendChild(createDate)
        header.appendChild(createTime)
        efmp.appendChild(header)
        # ----消息体信息----
        body = doc.createElement('body')
        paramSet = doc.createElement('paramSet')

        # -----每笔付款信息----
        param = doc.createElement('param')

        requestId = doc.createElement('requestId')
        requestId.appendChild(doc.createTextNode(payment.form_code))  # 单笔唯一标识
        param.appendChild(requestId)
        noteNo = doc.createElement('noteNo')
        noteNo.appendChild(doc.createTextNode(payment.partner_number))  # 客户单据号（非必填）
        param.appendChild(noteNo)
        transNo = doc.createElement('transNo')
        transNo.appendChild(doc.createTextNode(payment.partner_number))  # 业务流水号（非必填）
        param.appendChild(transNo)
        payUnitNo = doc.createElement('payUnitNo')
        payUnitNo.appendChild(doc.createTextNode(public_account.costomer_number))  # 付款方客户编号
        param.appendChild(payUnitNo)
        payUnitName = doc.createElement('payUnitName')
        payUnitName.appendChild(doc.createTextNode(public_account.costomer_name))  # 付款方客户名称
        param.appendChild(payUnitName)
        payAcntNo = doc.createElement('payAcntNo')
        payAcntNo.appendChild(doc.createTextNode(public_account.payment_number))  # 付款方账号
        param.appendChild(payAcntNo)
        payAcntName = doc.createElement('payAcntName')
        payAcntName.appendChild(doc.createTextNode(public_account.payment_username))  # 付款方户名
        param.appendChild(payAcntName)
        if payment.partner_number:
            recUnitNo = doc.createElement('recUnitNo')
            recUnitNo.appendChild(doc.createTextNode(payment.partner_number))  # 收款客户编号（非必填"
            param.appendChild(recUnitNo)
        if payment.partner_id:
            recUnitName = doc.createElement('recUnitName')
            recUnitName.appendChild(doc.createTextNode(payment.partner_id))  # 收款客户名称（非必填
            param.appendChild(recUnitName)
        recAcntNo = doc.createElement('recAcntNo')
        recAcntNo.appendChild(doc.createTextNode(payment.partner_bank_number))  # 收款方账号
        param.appendChild(recAcntNo)
        recAcntName = doc.createElement('recAcntName')
        recAcntName.appendChild(doc.createTextNode(payment.partner_id))  # 收款方户名
        param.appendChild(recAcntName)
        # 判断是否对外转账
        if payment.payee_identi == '01':
            recBankCode = doc.createElement('recBankCode')
            recBankCode.appendChild(doc.createTextNode(payment.payee_bank_code))  # 收款方银行代码（对外时必填）
            param.appendChild(recBankCode)
            recBankName = doc.createElement('recBankName')
            recBankName.appendChild(doc.createTextNode(payment.payee_bank))  # 收款银行名称（对外时必填）
            param.appendChild(recBankName)
            recBranchCode = doc.createElement('recBranchCode')
            recBranchCode.appendChild(doc.createTextNode(payment.payee_opening_bank_code))  # 收款方开户行（对外时必填）
            param.appendChild(recBranchCode)
            recBranchName = doc.createElement('recBranchName')
            recBranchName.appendChild(doc.createTextNode(payment.payee_opening_bank))  # 收款方开户行名称（对外时必填）
            param.appendChild(recBranchName)
            recProvinceCode = doc.createElement('recProvinceCode')
            recProvinceCode.appendChild(doc.createTextNode(payment.payee_opening_province_code))  # 收款方省份代码（非必填）
            param.appendChild(recProvinceCode)
            recProvinceName = doc.createElement('recProvinceName')
            recProvinceName.appendChild(doc.createTextNode(payment.payee_opening_province))  # 收款方省份名称（非必填）
            param.appendChild(recProvinceName)
            recCityCode = doc.createElement('recCityCode')
            recCityCode.appendChild(doc.createTextNode(payment.payee_opening_city_code))  # 收款方城市代码（非必填）
            param.appendChild(recCityCode)
            recCityName = doc.createElement('recCityName')
            recCityName.appendChild(doc.createTextNode(payment.payee_opening_city))  # 收款方城市名称（非必填）
            param.appendChild(recCityName)
        if payment.partner_contact:
            recLinkman = doc.createElement('recLinkman')
            recLinkman.appendChild(doc.createTextNode(payment.partner_contact))  # 收款方联系人（非必填）
            param.appendChild(recLinkman)
        if payment.partner_contact_phone:
            recLinkPhone = doc.createElement('recLinkPhone')
            recLinkPhone.appendChild(doc.createTextNode(payment.partner_contact_phone))  # 收款方联系电话（非必填）
            param.appendChild(recLinkPhone)
        if payment.partner_contact_add:
            recLinkAddress = doc.createElement('recLinkAddress')
            recLinkAddress.appendChild(doc.createTextNode(payment.partner_contact_add))  # 收款方联系地址（非必填）
            param.appendChild(recLinkAddress)
        if payment.pay_summary:
            recRemark = doc.createElement('recRemark')
            recRemark.appendChild(doc.createTextNode(payment.pay_summary))  # 收款方备注（非必填）
            param.appendChild(recRemark)
        if payment.currency_type.code:
            currencyCode = doc.createElement('currencyCode')
            currencyCode.appendChild(doc.createTextNode(payment.currency_type.code))  # 币种
            param.appendChild(currencyCode)
        amount = doc.createElement('amount')
        amount.appendChild(doc.createTextNode(str(payment.pay_money)))  # 付款金额
        param.appendChild(amount)
        txnDate = doc.createElement('txnDate')
        txnDate.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d')))  # 交易日期YYYYmmdd
        param.appendChild(txnDate)
        if payment.pay_use:
            payUse = doc.createElement('payUse')
            payUse.appendChild(doc.createTextNode(payment.pay_use))  # 付款用途 非必填
            param.appendChild(payUse)
        if payment.payment_model:
            payMode = doc.createElement('payMode')
            payMode.appendChild(doc.createTextNode(payment.payment_model))  # 付款模式（非必填）
            param.appendChild(payMode)
        if payment.pay_summary:
            summary = doc.createElement('summary')
            summary.appendChild(doc.createTextNode(payment.pay_summary))  # 付款摘要（非必填）
            param.appendChild(summary)
        corpFlag = doc.createElement('corpFlag')
        corpFlag.appendChild(doc.createTextNode(payment.public_signs))  # 公私标识
        param.appendChild(corpFlag)
        recFlag = doc.createElement('recFlag')
        recFlag.appendChild(doc.createTextNode(payment.payee_identi))  # 收款方标识
        param.appendChild(recFlag)
        # 加入每笔付款
        paramSet.appendChild(param)
        # 加入到body
        body.appendChild(paramSet)
        # 添加到跟元素中
        efmp.appendChild(body)
        doc.appendChild(efmp)
        return doc.toprettyxml(encoding='utf-8')

    @classmethod
    def package_bank_account_payment_to_xml(cls, payment, public_account):
        """封装成财企通银行账户付款的xml字符串（10005）
        :param payment: 付款单
        :param public_account: 付款确认向导
        :return string: 付款xml字符串
        """
        csystem_code = request.env['ir.values'].get_default('interface.bank.settings', 'p_csystem_code')
        csystem_name = request.env['ir.values'].get_default('interface.bank.settings', 'p_csystem_name')
        now_time = datetime.datetime.now()

        doc = xml.dom.minidom.Document()
        # 根元素以及属性
        efmp = doc.createElement('efmp')
        efmp.setAttribute('standard', 'FEG')
        efmp.setAttribute('type', '10005')
        efmp.setAttribute('version', '1.0')
        # -----头部信息----
        header = doc.createElement('header')
        appCode = doc.createElement('appCode')
        appCode.appendChild(doc.createTextNode(csystem_code))  # 接入系统代码
        appName = doc.createElement('appName')
        appName.appendChild(doc.createTextNode(csystem_name))  # 接入系统名称
        packageId = doc.createElement('packageId')
        packageId.appendChild(doc.createTextNode(payment.form_code))  # 报文标识号
        createDate = doc.createElement('createDate')
        createDate.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d')))  # 报文日期（yyyyMMdd）
        createTime = doc.createElement('createTime')
        createTime.appendChild(doc.createTextNode(now_time.strftime('%H%M%S')))  # 提交时间（HHmmss）
        header.appendChild(appCode)
        header.appendChild(appName)
        header.appendChild(packageId)
        header.appendChild(createDate)
        header.appendChild(createTime)
        efmp.appendChild(header)
        # ----消息体信息----
        body = doc.createElement('body')
        paramSet = doc.createElement('paramSet')

        # -----每笔付款信息----
        param = doc.createElement('param')

        requestId = doc.createElement('requestId')
        requestId.appendChild(doc.createTextNode(payment.form_code))  # 单笔唯一标识
        param.appendChild(requestId)
        payAcntNo = doc.createElement('payAcntNo')
        payAcntNo.appendChild(doc.createTextNode(public_account.payment_number))  # 付款方账号
        param.appendChild(payAcntNo)
        payAcntName = doc.createElement('payAcntName')
        payAcntName.appendChild(doc.createTextNode(public_account.payment_username))  # 付款方户名
        param.appendChild(payAcntName)
        payBankCode = doc.createElement('payBankCode')
        payBankCode.appendChild(doc.createTextNode(public_account.payment_bank.code))  # 付款方银行类别代码
        param.appendChild(payBankCode)
        payBankName = doc.createElement('payBankName')
        payBankName.appendChild(doc.createTextNode(public_account.payment_bank.name))  # 付款银行名称
        param.appendChild(payBankName)
        payBankBranch = doc.createElement('payBankBranch')
        payBankBranch.appendChild(doc.createTextNode(public_account.deposit_id.code))  # 付款方开户行号
        param.appendChild(payBankBranch)
        payBankBranchName = doc.createElement('payBankBranchName')
        payBankBranchName.appendChild(doc.createTextNode(public_account.deposit_id.name))  # 付款方开户行名称
        param.appendChild(payBankBranchName)
        payZoneCode = doc.createElement('payZoneCode')
        payZoneCode.appendChild(doc.createTextNode(public_account.city_id.code if public_account.city_id.code else '22'))  # 付款方地区代码
        param.appendChild(payZoneCode)
        payAcntCls = doc.createElement('payAcntCls')
        # 为了适应00-0和01-1，在此进行判断转换
        if payment.public_signs == '00':
            payAcntCls.appendChild(doc.createTextNode('0'))  # 付款方类别  0:对公1:对私
        else:
            payAcntCls.appendChild(doc.createTextNode('1'))  # 付款方类别  0:对公1:对私
        param.appendChild(payAcntCls)
        # payAddr = doc.createElement('payAddr')
        # payAddr.appendChild(doc.createTextNode(payment.company_id.))  # 付款方地址-否
        # param.appendChild(payAddr)
        recOrgName = doc.createElement('recOrgName')
        recOrgName.appendChild(doc.createTextNode(payment.company_id.name))  # 收款方机构名称-否
        param.appendChild(recOrgName)
        recAcntNo = doc.createElement('recAcntNo')
        recAcntNo.appendChild(doc.createTextNode(payment.partner_bank_number))  # 收款方账号
        param.appendChild(recAcntNo)
        recAcntName = doc.createElement('recAcntName')
        recAcntName.appendChild(doc.createTextNode(payment.partner_id))  # 收款方户名
        param.appendChild(recAcntName)
        recBankCode = doc.createElement('recBankCode')
        recBankCode.appendChild(doc.createTextNode(payment.payee_bank_code))  # 收款方银行类别代码
        param.appendChild(recBankCode)
        recBankName = doc.createElement('recBankName')
        recBankName.appendChild(doc.createTextNode(payment.payee_bank))  # 收款方银行名称
        param.appendChild(recBankName)
        recBankBranch = doc.createElement('recBankBranch')
        recBankBranch.appendChild(doc.createTextNode(payment.payee_opening_bank_code))  # 收款方开户行号
        param.appendChild(recBankBranch)
        recBankBranchName = doc.createElement('recBankBranchName')
        recBankBranchName.appendChild(doc.createTextNode(payment.payee_opening_bank))  # 收款方开户行名称
        param.appendChild(recBankBranchName)
        recZoneCode = doc.createElement('recZoneCode')
        recZoneCode.appendChild(doc.createTextNode(payment.payee_opening_city_code))  # 收款方地区代码
        param.appendChild(recZoneCode)
        recAcntCls = doc.createElement('recAcntCls')
        # 适应并转换
        if payment.public_signs == '00':
            recAcntCls.appendChild(doc.createTextNode('0'))  # 收款方类别
        else:
            recAcntCls.appendChild(doc.createTextNode('1'))  # 收款方类别
        param.appendChild(recAcntCls)
        recAddr = doc.createElement('recAddr')
        recAddr.appendChild(
            doc.createTextNode(payment.payee_opening_province + '-' + payment.payee_opening_city))  # 收款方地址
        param.appendChild(recAddr)
        amount = doc.createElement('amount')
        amount.appendChild(doc.createTextNode(str(payment.pay_money)))  # 金额
        param.appendChild(amount)
        currencyCode = doc.createElement('currencyCode')
        currencyCode.appendChild(doc.createTextNode(payment.currency_type.code))  # 币种
        param.appendChild(currencyCode)
        if payment.pay_use:
            payUse = doc.createElement('payUse')
            payUse.appendChild(doc.createTextNode(payment.pay_use))  # 付款用途
            param.appendChild(payUse)
        postScript = doc.createElement('postScript')
        if payment.pay_summary:
            postScript.appendChild(doc.createTextNode(payment.pay_summary))  # 附言
        param.appendChild(postScript)
        acrossBankFlag = doc.createElement('acrossBankFlag')
        acrossBankFlag.appendChild(doc.createTextNode(payment.cross_row_identi))  # 跨行标识
        param.appendChild(acrossBankFlag)
        diffPlaceFlag = doc.createElement('diffPlaceFlag')
        diffPlaceFlag.appendChild(doc.createTextNode(payment.off_site_identi))  # 异地标识
        param.appendChild(diffPlaceFlag)
        paySpeed = doc.createElement('paySpeed')
        # 适应转换  01 - 0：普通速度  02-1：加快速度
        if payment.payment_model == '01':
            paySpeed.appendChild(doc.createTextNode('0'))  # 付款速度
        elif payment.payment_model == '02':
            paySpeed.appendChild(doc.createTextNode('1'))  # 付款速度
        param.appendChild(paySpeed)

        # 加入每笔付款
        paramSet.appendChild(param)
        # 加入到body
        body.appendChild(paramSet)
        # 添加到跟元素中
        efmp.appendChild(body)
        doc.appendChild(efmp)
        return doc.toprettyxml(encoding='utf-8')

    @classmethod
    def package_query_payment_result_to_xml(cls, number_array):
        """将付款单编号封装成财企通查询付款结果xml(80001)
        :param number_array: 付款单编号数组
        """
        csystem_code = request.env['ir.values'].get_default('interface.bank.settings', 'p_csystem_code')
        csystem_name = request.env['ir.values'].get_default('interface.bank.settings', 'p_csystem_name')
        now_time = datetime.datetime.now()
        doc = xml.dom.minidom.Document()
        # 根元素以及属性
        efmp = doc.createElement('efmp')
        efmp.setAttribute('standard', 'FEG')
        efmp.setAttribute('type', '80001')
        efmp.setAttribute('version', '1.0')
        # -----头部信息----
        header = doc.createElement('header')
        appCode = doc.createElement('appCode')
        appCode.appendChild(doc.createTextNode(csystem_code))  # 接入系统代码
        appName = doc.createElement('appName')
        appName.appendChild(doc.createTextNode(csystem_name))  # 接入系统名称
        packageId = doc.createElement('packageId')
        packageId.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d%H%M%S')))  # 报文标识号
        createDate = doc.createElement('createDate')
        createDate.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d')))  # 报文日期（yyyyMMdd）
        createTime = doc.createElement('createTime')
        createTime.appendChild(doc.createTextNode(now_time.strftime('%H%M%S')))  # 提交时间（HHmmss）
        header.appendChild(appCode)
        header.appendChild(appName)
        header.appendChild(packageId)
        header.appendChild(createDate)
        header.appendChild(createTime)
        efmp.appendChild(header)
        # ----消息体信息----
        body = doc.createElement('body')
        paramSet = doc.createElement('paramSet')
        # 循环编号数组
        for number in number_array:
            # -----每笔付款信息----
            param = doc.createElement('param')
            requestId = doc.createElement('requestId')
            requestId.appendChild(doc.createTextNode(number))  # 单笔唯一标识
            param.appendChild(requestId)
            # # 加入每笔付款
            paramSet.appendChild(param)
        # 加入到body
        body.appendChild(paramSet)
        # 添加到跟元素中
        efmp.appendChild(body)
        doc.appendChild(efmp)
        return doc.toprettyxml(encoding='utf-8')

    @classmethod
    def package_electronic_return_inquiry(cls, res):
        """封装财企通查询电子回单接口(20001)
        :param res: 查询信息
        """
        csystem_code = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_code')
        csystem_name = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_name')
        now_time = datetime.datetime.now()

        doc = xml.dom.minidom.Document()
        # 根元素以及属性
        efmp = doc.createElement('efmp')
        efmp.setAttribute('standard', 'FEG')
        efmp.setAttribute('type', '20001')
        efmp.setAttribute('version', '1.0')
        # -----头部信息----
        header = doc.createElement('header')
        appCode = doc.createElement('appCode')
        appCode.appendChild(doc.createTextNode(csystem_code))  # 接入系统代码
        appName = doc.createElement('appName')
        appName.appendChild(doc.createTextNode(csystem_name))  # 接入系统名称
        packageId = doc.createElement('packageId')
        packageId.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d%H%M%S')))  # 报文标识号
        createDate = doc.createElement('createDate')
        createDate.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d')))  # 报文日期（yyyyMMdd）
        createTime = doc.createElement('createTime')
        createTime.appendChild(doc.createTextNode(now_time.strftime('%H%M%S')))  # 提交时间（HHmmss）
        offset = doc.createElement('offset')
        offset.appendChild(doc.createTextNode(str(res.get('offset'))))  # 起始记录数
        pageSize = doc.createElement('pageSize')
        pageSize.appendChild(doc.createTextNode(str(res.get('pageSize'))))  # 页记录数
        header.appendChild(appCode)
        header.appendChild(appName)
        header.appendChild(packageId)
        header.appendChild(createDate)
        header.appendChild(createTime)
        header.appendChild(offset)
        header.appendChild(pageSize)
        efmp.appendChild(header)
        # ----消息体信息----
        body = doc.createElement('body')
        paramSet = doc.createElement('paramSet')

        param = doc.createElement('param')
        custNo = doc.createElement('custNo')
        custNo.appendChild(doc.createTextNode(res.get('custNo')))  # 客户编号
        param.appendChild(custNo)
        custName = doc.createElement('custName')
        custName.appendChild(doc.createTextNode(res.get('custName')))  # 客户名称
        param.appendChild(custName)
        slipId = doc.createElement('slipId')
        slipId.appendChild(doc.createTextNode(res.get('slipId')))  # 电子回单唯一标识
        param.appendChild(slipId)
        slipNo = doc.createElement('slipNo')
        slipNo.appendChild(doc.createTextNode(res.get('slipNo')))  # 电子回单号
        param.appendChild(slipNo)
        start_date = datetime.datetime.strptime(res.get('startDate'), '%Y-%m-%d')
        startDate = doc.createElement('startDate')
        startDate.appendChild(doc.createTextNode(start_date.strftime('%Y%m%d')))  # 开始日期
        param.appendChild(startDate)
        end_date = datetime.datetime.strptime(res.get('endDate'), '%Y-%m-%d')
        endDate = doc.createElement('endDate')
        endDate.appendChild(doc.createTextNode(end_date.strftime('%Y%m%d')))  # 结束日期
        param.appendChild(endDate)

        # # 加入
        paramSet.appendChild(param)
        # 加入到body
        body.appendChild(paramSet)
        # 添加到跟元素中
        efmp.appendChild(body)
        doc.appendChild(efmp)
        return doc.toprettyxml(encoding='utf-8')

    @classmethod
    def package_query_internal_account_transaction_details_to_xml(cls, account, search):
        """封装内部账户交易明细查询xml（20003）
        :param account: 选择的账户
        :param search: 查询对象
        :return string :xml
        """
        csystem_code = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_code')
        csystem_name = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_name')
        now_time = datetime.datetime.now()

        doc = xml.dom.minidom.Document()
        # 根元素以及属性
        efmp = doc.createElement('efmp')
        efmp.setAttribute('standard', 'FEG')
        efmp.setAttribute('type', '20003')
        efmp.setAttribute('version', '1.0')
        # -----头部信息----
        header = doc.createElement('header')
        appCode = doc.createElement('appCode')
        appCode.appendChild(doc.createTextNode(csystem_code))  # 接入系统代码
        appName = doc.createElement('appName')
        appName.appendChild(doc.createTextNode(csystem_name))  # 接入系统名称
        packageId = doc.createElement('packageId')
        packageId.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d%H%M%S')))  # 报文标识号
        createDate = doc.createElement('createDate')
        createDate.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d')))  # 报文日期（yyyyMMdd）
        createTime = doc.createElement('createTime')
        createTime.appendChild(doc.createTextNode(now_time.strftime('%H%M%S')))  # 提交时间（HHmmss）
        header.appendChild(appCode)
        header.appendChild(appName)
        header.appendChild(packageId)
        header.appendChild(createDate)
        header.appendChild(createTime)
        efmp.appendChild(header)
        # ----消息体信息----
        body = doc.createElement('body')
        paramSet = doc.createElement('paramSet')
        param = doc.createElement('param')
        if account.costomer_number:
            custNo = doc.createElement('custNo')
            custNo.appendChild(doc.createTextNode(account.costomer_number))  # 客户编号
            param.appendChild(custNo)
        if account.costomer_name:
            custName = doc.createElement('custName')
            custName.appendChild(doc.createTextNode(account.costomer_name))  # 客户名称
            param.appendChild(custName)
        if account.payment_number:
            acntNo = doc.createElement('acntNo')
            acntNo.appendChild(doc.createTextNode(account.payment_number))  # 账号
            param.appendChild(acntNo)
        if account.payment_username:
            acntName = doc.createElement('acntName')
            acntName.appendChild(doc.createTextNode(account.payment_username))  # 户名
            param.appendChild(acntName)
        if search.startDate:
            startDate = doc.createElement('startDate')
            start_date = datetime.datetime.strptime(search.startDate, '%Y-%m-%d')
            startDate.appendChild(doc.createTextNode(start_date.strftime('%Y%m%d')))  # 开始日期
            param.appendChild(startDate)
        if search.endDate:
            endDate = doc.createElement('endDate')
            end_date = datetime.datetime.strptime(search.endDate, '%Y-%m-%d')
            endDate.appendChild(doc.createTextNode(end_date.strftime('%Y%m%d')))  # 结束日期
            param.appendChild(endDate)
        if search.transId:
            transId = doc.createElement('transId')
            transId.appendChild(doc.createTextNode(search.transId))  # 交易ID
            param.appendChild(transId)
        paramSet.appendChild(param)
        # 加入到body
        body.appendChild(paramSet)
        # 添加到跟元素中
        efmp.appendChild(body)
        doc.appendChild(efmp)
        return doc.toprettyxml(encoding='utf-8')

    @classmethod
    def package_query_bank_account_transaction_details(cls, external_id, search):
        """封装银行账户交易明细查询xml(20007)
        """
        csystem_code = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_code')
        csystem_name = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_name')
        now_time = datetime.datetime.now()

        doc = xml.dom.minidom.Document()
        # 根元素以及属性
        efmp = doc.createElement('efmp')
        efmp.setAttribute('standard', 'FEG')
        efmp.setAttribute('type', '20007')
        efmp.setAttribute('version', '1.0')
        # -----头部信息----
        header = doc.createElement('header')
        appCode = doc.createElement('appCode')
        appCode.appendChild(doc.createTextNode(csystem_code))  # 接入系统代码
        appName = doc.createElement('appName')
        appName.appendChild(doc.createTextNode(csystem_name))  # 接入系统名称
        packageId = doc.createElement('packageId')
        packageId.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d%H%M%S')))  # 报文标识号
        createDate = doc.createElement('createDate')
        createDate.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d')))  # 报文日期（yyyyMMdd）
        createTime = doc.createElement('createTime')
        createTime.appendChild(doc.createTextNode(now_time.strftime('%H%M%S')))  # 提交时间（HHmmss）
        header.appendChild(appCode)
        header.appendChild(appName)
        header.appendChild(packageId)
        header.appendChild(createDate)
        header.appendChild(createTime)
        efmp.appendChild(header)
        # ----消息体信息----
        body = doc.createElement('body')
        paramSet = doc.createElement('paramSet')
        param = doc.createElement('param')
        if external_id.account_id.costomer_number:
            custNo = doc.createElement('custNo')
            custNo.appendChild(doc.createTextNode(external_id.account_id.costomer_number))  # 客户编号
            param.appendChild(custNo)
        if external_id.account_id.costomer_name:
            custName = doc.createElement('custName')
            custName.appendChild(doc.createTextNode(external_id.account_id.costomer_name))  # 客户名称
            param.appendChild(custName)
        if external_id.e_bank_number:
            bankAcntNo = doc.createElement('bankAcntNo')
            bankAcntNo.appendChild(doc.createTextNode(external_id.e_bank_number))  # 银行账号
            param.appendChild(bankAcntNo)
        if external_id.e_bank_name:
            bankAcntName = doc.createElement('bankAcntName')
            bankAcntName.appendChild(doc.createTextNode(external_id.e_bank_name))  # 银行账户名
            param.appendChild(bankAcntName)
        if search.startDate:
            startDate = doc.createElement('startDate')
            start_date = datetime.datetime.strptime(search.startDate, '%Y-%m-%d')
            startDate.appendChild(doc.createTextNode(start_date.strftime('%Y%m%d')))  # 开始日期
            param.appendChild(startDate)
        if search.endDate:
            endDate = doc.createElement('endDate')
            end_date = datetime.datetime.strptime(search.endDate, '%Y-%m-%d')
            endDate.appendChild(doc.createTextNode(end_date.strftime('%Y%m%d')))  # 结束日期
            param.appendChild(endDate)
        paramSet.appendChild(param)
        # 加入到body
        body.appendChild(paramSet)
        # 添加到跟元素中
        efmp.appendChild(body)
        doc.appendChild(efmp)
        return doc.toprettyxml(encoding='utf-8')

    @classmethod
    def package_query_position_account_transaction_details(cls, account, search):
        """封装头寸账户查询交易明细xml（20017）
        """
        csystem_code = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_code')
        csystem_name = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_name')
        now_time = datetime.datetime.now()
        doc = xml.dom.minidom.Document()
        # 根元素以及属性
        efmp = doc.createElement('efmp')
        efmp.setAttribute('standard', 'FEG')
        efmp.setAttribute('type', '20017')
        efmp.setAttribute('version', '1.0')
        # -----头部信息----
        header = doc.createElement('header')
        appCode = doc.createElement('appCode')
        appCode.appendChild(doc.createTextNode(csystem_code))  # 接入系统代码
        appName = doc.createElement('appName')
        appName.appendChild(doc.createTextNode(csystem_name))  # 接入系统名称
        packageId = doc.createElement('packageId')
        packageId.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d%H%M%S')))  # 报文标识号
        createDate = doc.createElement('createDate')
        createDate.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d')))  # 报文日期（yyyyMMdd）
        createTime = doc.createElement('createTime')
        createTime.appendChild(doc.createTextNode(now_time.strftime('%H%M%S')))  # 提交时间（HHmmss）
        header.appendChild(appCode)
        header.appendChild(appName)
        header.appendChild(packageId)
        header.appendChild(createDate)
        header.appendChild(createTime)
        efmp.appendChild(header)
        # ----消息体信息----
        body = doc.createElement('body')
        paramSet = doc.createElement('paramSet')
        param = doc.createElement('param')
        if account.payment_number:
            bankAcntNo = doc.createElement('bankAcntNo')
            bankAcntNo.appendChild(doc.createTextNode(account.payment_number))  # 头寸账号
            param.appendChild(bankAcntNo)
        if account.payment_username:
            bankAcntName = doc.createElement('bankAcntName')
            bankAcntName.appendChild(doc.createTextNode(account.payment_username))  # 头寸账户名
            param.appendChild(bankAcntName)
        if search.startDate:
            startDate = doc.createElement('startDate')
            start_date = datetime.datetime.strptime(search.startDate, '%Y-%m-%d')
            startDate.appendChild(doc.createTextNode(start_date.strftime('%Y%m%d')))  # 开始日期
            param.appendChild(startDate)
        if search.endDate:
            endDate = doc.createElement('endDate')
            end_date = datetime.datetime.strptime(search.endDate, '%Y-%m-%d')
            endDate.appendChild(doc.createTextNode(end_date.strftime('%Y%m%d')))  # 结束日期
            param.appendChild(endDate)
        paramSet.appendChild(param)
        # 加入到body
        body.appendChild(paramSet)
        # 添加到跟元素中
        efmp.appendChild(body)
        doc.appendChild(efmp)
        return doc.toprettyxml(encoding='utf-8')

    @classmethod
    def package_query_internal_account_balance(cls, account):
        """封装查询内部账户余额为xml(20005)
        :param account: 付款账户
        :return string
        """
        csystem_code = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_code')
        csystem_name = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_name')
        now_time = datetime.datetime.now()
        doc = xml.dom.minidom.Document()
        # 根元素以及属性
        efmp = doc.createElement('efmp')
        efmp.setAttribute('standard', 'FEG')
        efmp.setAttribute('type', '20005')
        efmp.setAttribute('version', '1.0')
        # -----头部信息----
        header = doc.createElement('header')
        appCode = doc.createElement('appCode')
        appCode.appendChild(doc.createTextNode(csystem_code))  # 接入系统代码
        appName = doc.createElement('appName')
        appName.appendChild(doc.createTextNode(csystem_name))  # 接入系统名称
        packageId = doc.createElement('packageId')
        packageId.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d%H%M%S')))  # 报文标识号
        createDate = doc.createElement('createDate')
        createDate.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d')))  # 报文日期（yyyyMMdd）
        createTime = doc.createElement('createTime')
        createTime.appendChild(doc.createTextNode(now_time.strftime('%H%M%S')))  # 提交时间（HHmmss）
        header.appendChild(appCode)
        header.appendChild(appName)
        header.appendChild(packageId)
        header.appendChild(createDate)
        header.appendChild(createTime)
        efmp.appendChild(header)
        # ----消息体信息----
        body = doc.createElement('body')
        paramSet = doc.createElement('paramSet')
        param = doc.createElement('param')
        if account.costomer_number:
            custNo = doc.createElement('custNo')
            custNo.appendChild(doc.createTextNode(account.costomer_number))  # 客户编号
            param.appendChild(custNo)
        if account.costomer_name:
            custName = doc.createElement('custName')
            custName.appendChild(doc.createTextNode(account.costomer_name))  # 客户名称
            param.appendChild(custName)
        if account.payment_number:
            acntNo = doc.createElement('acntNo')
            acntNo.appendChild(doc.createTextNode(account.payment_number))  # 内部账户
            param.appendChild(acntNo)
        if account.payment_username:
            acntName = doc.createElement('acntName')
            acntName.appendChild(doc.createTextNode(account.payment_username))  # 账户名称
            param.appendChild(acntName)
        paramSet.appendChild(param)
        # 加入到body
        body.appendChild(paramSet)
        # 添加到跟元素中
        efmp.appendChild(body)
        doc.appendChild(efmp)
        return doc.toprettyxml(encoding='utf-8')

    @classmethod
    def package_search_bank_account_balance(cls, externals):
        """封装查询银行账户余额为xml(20009)
        :param externals: 银行账户
        :return string
        """
        csystem_code = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_code')
        csystem_name = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_name')
        now_time = datetime.datetime.now()
        doc = xml.dom.minidom.Document()
        # 根元素以及属性
        efmp = doc.createElement('efmp')
        efmp.setAttribute('standard', 'FEG')
        efmp.setAttribute('type', '20009')
        efmp.setAttribute('version', '1.0')
        # -----头部信息----
        header = doc.createElement('header')
        appCode = doc.createElement('appCode')
        appCode.appendChild(doc.createTextNode(csystem_code))  # 接入系统代码
        appName = doc.createElement('appName')
        appName.appendChild(doc.createTextNode(csystem_name))  # 接入系统名称
        packageId = doc.createElement('packageId')
        packageId.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d%H%M%S')))  # 报文标识号
        createDate = doc.createElement('createDate')
        createDate.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d')))  # 报文日期（yyyyMMdd）
        createTime = doc.createElement('createTime')
        createTime.appendChild(doc.createTextNode(now_time.strftime('%H%M%S')))  # 提交时间（HHmmss）
        header.appendChild(appCode)
        header.appendChild(appName)
        header.appendChild(packageId)
        header.appendChild(createDate)
        header.appendChild(createTime)
        efmp.appendChild(header)
        # ----消息体信息----
        body = doc.createElement('body')
        paramSet = doc.createElement('paramSet')
        param = doc.createElement('param')
        if externals.account_id.costomer_number:
            custNo = doc.createElement('custNo')
            custNo.appendChild(doc.createTextNode(externals.account_id.costomer_number))  # 客户编号
            param.appendChild(custNo)
        if externals.account_id.costomer_name:
            custName = doc.createElement('custName')
            custName.appendChild(doc.createTextNode(externals.account_id.costomer_name))  # 客户名称
            param.appendChild(custName)
        if externals.e_bank_number:
            bankAcntNo = doc.createElement('bankAcntNo')
            bankAcntNo.appendChild(doc.createTextNode(externals.e_bank_number))  # 银行账户
            param.appendChild(bankAcntNo)
        if externals.e_bank_name:
            bankAcntName = doc.createElement('bankAcntName')
            bankAcntName.appendChild(doc.createTextNode(externals.e_bank_name))  # 银行名称
            param.appendChild(bankAcntName)
        paramSet.appendChild(param)
        # 加入到body
        body.appendChild(paramSet)
        # 添加到跟元素中
        efmp.appendChild(body)
        doc.appendChild(efmp)
        return doc.toprettyxml(encoding='utf-8')

    @classmethod
    def package_search_money_supply_account_balance(cls, account):
        """封装查询头寸账户余额为xml(20019)
        :param account: 付款账户
        :return string
        """
        csystem_code = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_code')
        csystem_name = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_name')
        now_time = datetime.datetime.now()
        doc = xml.dom.minidom.Document()
        # 根元素以及属性
        efmp = doc.createElement('efmp')
        efmp.setAttribute('standard', 'FEG')
        efmp.setAttribute('type', '20019')
        efmp.setAttribute('version', '1.0')
        # -----头部信息----
        header = doc.createElement('header')
        appCode = doc.createElement('appCode')
        appCode.appendChild(doc.createTextNode(csystem_code))  # 接入系统代码
        appName = doc.createElement('appName')
        appName.appendChild(doc.createTextNode(csystem_name))  # 接入系统名称
        packageId = doc.createElement('packageId')
        packageId.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d%H%M%S')))  # 报文标识号
        createDate = doc.createElement('createDate')
        createDate.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d')))  # 报文日期（yyyyMMdd）
        createTime = doc.createElement('createTime')
        createTime.appendChild(doc.createTextNode(now_time.strftime('%H%M%S')))  # 提交时间（HHmmss）
        header.appendChild(appCode)
        header.appendChild(appName)
        header.appendChild(packageId)
        header.appendChild(createDate)
        header.appendChild(createTime)
        efmp.appendChild(header)
        # ----消息体信息----
        body = doc.createElement('body')
        paramSet = doc.createElement('paramSet')
        param = doc.createElement('param')
        if account.payment_number:
            bankAcntNo = doc.createElement('bankAcntNo')
            bankAcntNo.appendChild(doc.createTextNode(account.payment_number))  # 头寸账户
            param.appendChild(bankAcntNo)
        if account.payment_username:
            bankAcntName = doc.createElement('bankAcntName')
            bankAcntName.appendChild(doc.createTextNode(account.payment_username))  # 头寸账户名称
            param.appendChild(bankAcntName)
        paramSet.appendChild(param)
        # 加入到body
        body.appendChild(paramSet)
        # 添加到跟元素中
        efmp.appendChild(body)
        doc.appendChild(efmp)
        return doc.toprettyxml(encoding='utf-8')

    @classmethod
    def package_query_the_company_number(cls, bank_code):
        """封装查询联行号xml(20011)"""
        csystem_code = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_code')
        csystem_name = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_name')
        now_time = datetime.datetime.now()
        doc = xml.dom.minidom.Document()
        # 根元素以及属性
        efmp = doc.createElement('efmp')
        efmp.setAttribute('standard', 'FEG')
        efmp.setAttribute('type', '20011')
        efmp.setAttribute('version', '1.0')
        # -----头部信息----
        header = doc.createElement('header')
        appCode = doc.createElement('appCode')
        appCode.appendChild(doc.createTextNode(csystem_code))  # 接入系统代码
        appName = doc.createElement('appName')
        appName.appendChild(doc.createTextNode(csystem_name))  # 接入系统名称
        packageId = doc.createElement('packageId')
        packageId.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d%H%M%S')))  # 报文标识号
        createDate = doc.createElement('createDate')
        createDate.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d')))  # 报文日期（yyyyMMdd）
        createTime = doc.createElement('createTime')
        createTime.appendChild(doc.createTextNode(now_time.strftime('%H%M%S')))  # 提交时间（HHmmss）
        header.appendChild(appCode)
        header.appendChild(appName)
        header.appendChild(packageId)
        header.appendChild(createDate)
        header.appendChild(createTime)
        efmp.appendChild(header)
        # ----消息体信息----
        body = doc.createElement('body')
        paramSet = doc.createElement('paramSet')
        param = doc.createElement('param')
        ownerBankCode = doc.createElement('ownerBankCode')
        if bank_code:
            ownerBankCode.appendChild(doc.createTextNode(bank_code))  # 银行代码
        else:
            ownerBankCode.appendChild(doc.createTextNode(''))  # 银行代码
        param.appendChild(ownerBankCode)
        paramSet.appendChild(param)
        # 加入到body
        body.appendChild(paramSet)
        # 添加到跟元素中
        efmp.appendChild(body)
        doc.appendChild(efmp)
        return doc.toprettyxml(encoding='utf-8')

    @classmethod
    def package_daily_fund_plan_to_xml(cls, search):
        """封装查询日资金计划xml并返回（20013）
        :param search : 查询对象
        :return string
        """
        csystem_code = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_code')
        csystem_name = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_name')
        now_time = datetime.datetime.now()
        doc = xml.dom.minidom.Document()
        # 根元素以及属性
        efmp = doc.createElement('efmp')
        efmp.setAttribute('standard', 'FEG')
        efmp.setAttribute('type', '20013')
        efmp.setAttribute('version', '1.0')
        # -----头部信息----
        header = doc.createElement('header')
        appCode = doc.createElement('appCode')
        appCode.appendChild(doc.createTextNode(csystem_code))  # 接入系统代码
        appName = doc.createElement('appName')
        appName.appendChild(doc.createTextNode(csystem_name))  # 接入系统名称
        packageId = doc.createElement('packageId')
        packageId.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d%H%M%S')))  # 报文标识号
        createDate = doc.createElement('createDate')
        createDate.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d')))  # 报文日期（yyyyMMdd）
        createTime = doc.createElement('createTime')
        createTime.appendChild(doc.createTextNode(now_time.strftime('%H%M%S')))  # 提交时间（HHmmss）
        header.appendChild(appCode)
        header.appendChild(appName)
        header.appendChild(packageId)
        header.appendChild(createDate)
        header.appendChild(createTime)
        efmp.appendChild(header)
        # ----消息体信息----
        body = doc.createElement('body')
        paramSet = doc.createElement('paramSet')
        param = doc.createElement('param')

        custNo = doc.createElement('custNo')
        custNo.appendChild(doc.createTextNode(search.custNo))  # 客户编号
        param.appendChild(custNo)

        plan_date = datetime.datetime.strptime(search.planDate, '%Y-%m-%d')
        planDate = doc.createElement('planDate')
        planDate.appendChild(doc.createTextNode(plan_date.strftime('%Y%m%d')))  # 计划日期yyyyMMdd
        param.appendChild(planDate)
        currencyCode = doc.createElement('currencyCode')
        currencyCode.appendChild(doc.createTextNode(search.currencyCode.code))  # 币种
        param.appendChild(currencyCode)
        paramSet.appendChild(param)
        # 加入到body
        body.appendChild(paramSet)
        # 添加到跟元素中
        efmp.appendChild(body)
        doc.appendChild(efmp)
        return doc.toprettyxml(encoding='utf-8')

    @classmethod
    def package_bill_storage_to_xml(cls, bill):
        """封装票据入库单位xml（30001）
        """
        csystem_code = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_code')
        csystem_name = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_name')
        now_time = datetime.datetime.now()
        doc = xml.dom.minidom.Document()
        # 根元素以及属性
        efmp = doc.createElement('efmp')
        efmp.setAttribute('standard', 'FEG')
        efmp.setAttribute('type', '30001')
        efmp.setAttribute('version', '1.0')
        # -----头部信息----
        header = doc.createElement('header')
        appCode = doc.createElement('appCode')
        appCode.appendChild(doc.createTextNode(csystem_code))  # 接入系统代码
        appName = doc.createElement('appName')
        appName.appendChild(doc.createTextNode(csystem_name))  # 接入系统名称
        packageId = doc.createElement('packageId')
        packageId.appendChild(doc.createTextNode(bill.requestId))  # 报文标识号
        createDate = doc.createElement('createDate')
        createDate.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d')))  # 报文日期（yyyyMMdd）
        createTime = doc.createElement('createTime')
        createTime.appendChild(doc.createTextNode(now_time.strftime('%H%M%S')))  # 提交时间（HHmmss）
        header.appendChild(appCode)
        header.appendChild(appName)
        header.appendChild(packageId)
        header.appendChild(createDate)
        header.appendChild(createTime)
        efmp.appendChild(header)
        # ----消息体信息----
        body = doc.createElement('body')
        paramSet = doc.createElement('paramSet')
        param = doc.createElement('param')

        requestId = doc.createElement('requestId')
        requestId.appendChild(doc.createTextNode(bill.requestId))  # 单笔唯一标识
        param.appendChild(requestId)
        batchId = doc.createElement('batchId')
        batchId.appendChild(doc.createTextNode(bill.batchId))  # 批次号
        param.appendChild(batchId)
        custNo = doc.createElement('custNo')
        custNo.appendChild(doc.createTextNode(bill.custNo))  # 持有人客户编号
        param.appendChild(custNo)
        custName = doc.createElement('custName')
        custName.appendChild(doc.createTextNode(bill.custName))  # 持有人客户名称
        param.appendChild(custName)

        draftSet = doc.createElement('draftSet')
        for line in bill.line_ids:
            draft = doc.createElement('draft')
            draftNo = doc.createElement('draftNo')
            draftNo.appendChild(doc.createTextNode(line.draftNo))  # 票据号
            draft.appendChild(draftNo)
            draftTp = doc.createElement('draftTp')
            draftTp.appendChild(doc.createTextNode(line.draftTp))  # 票据种类
            draft.appendChild(draftTp)
            draftCls = doc.createElement('draftCls')
            draftCls.appendChild(doc.createTextNode(line.draftCls))  # 票据类型
            draft.appendChild(draftCls)
            draftSource = doc.createElement('draftSource')
            draftSource.appendChild(doc.createTextNode(line.draftSource))  # 票据来源
            draft.appendChild(draftSource)
            isse_date = datetime.datetime.strptime(line.isseDate, '%Y-%m-%d')
            isseDate = doc.createElement('isseDate')
            isseDate.appendChild(doc.createTextNode(isse_date.strftime('%Y%m%d')))  # 出票日
            draft.appendChild(isseDate)
            due_date = datetime.datetime.strptime(line.dueDate, '%Y-%m-%d')
            dueDate = doc.createElement('dueDate')
            dueDate.appendChild(doc.createTextNode(due_date.strftime('%Y%m%d')))  # 到期日
            draft.appendChild(dueDate)
            if line.accptrDate:
                accptr_date = datetime.datetime.strptime(line.accptrDate, '%Y-%m-%d')
                accptrDate = doc.createElement('accptrDate')
                accptrDate.appendChild(doc.createTextNode(accptr_date.strftime('%Y%m%d')))  # 承兑日期
                draft.appendChild(accptrDate)
            isseAmt = doc.createElement('isseAmt')
            isseAmt.appendChild(doc.createTextNode(line.isseAmt))  # 票面金额
            draft.appendChild(isseAmt)
            drwrAcnt = doc.createElement('drwrAcnt')
            if line.drwrAcnt:
                drwrAcnt.appendChild(doc.createTextNode(line.drwrAcnt))  # 出票人账户
            draft.appendChild(drwrAcnt)
            drwrName = doc.createElement('drwrName')
            drwrName.appendChild(doc.createTextNode(line.drwrName))  # 出票人名称
            draft.appendChild(drwrName)
            pyeeAcnt = doc.createElement('pyeeAcnt')
            if line.pyeeAcnt:
                pyeeAcnt.appendChild(doc.createTextNode(line.pyeeAcnt))  # 收票人账户
            draft.appendChild(pyeeAcnt)
            pyeeName = doc.createElement('pyeeName')
            if line.pyeeName:
                pyeeName.appendChild(doc.createTextNode(line.pyeeName))  # 收票人名称
            draft.appendChild(pyeeName)
            pyeeAcctsvcr = doc.createElement('pyeeAcctsvcr')
            if line.pyeeAcctsvcr:
                pyeeAcctsvcr.appendChild(doc.createTextNode(line.pyeeAcctsvcr))  # 收票人开户行号
            draft.appendChild(pyeeAcctsvcr)
            pyeeAcctsvcrName = doc.createElement('pyeeAcctsvcrName')
            if line.pyeeAcctsvcrName:
                pyeeAcctsvcrName.appendChild(doc.createTextNode(line.pyeeAcctsvcrName))  # 收票人开户行名
            draft.appendChild(pyeeAcctsvcrName)
            accptrAcnt = doc.createElement('accptrAcnt')
            if line.accptrAcnt:
                accptrAcnt.appendChild(doc.createTextNode(line.accptrAcnt))  # 承兑人/行账户
            draft.appendChild(accptrAcnt)
            accptrName = doc.createElement('accptrName')
            if line.accptrName:
                accptrName.appendChild(doc.createTextNode(line.accptrName))  # 承兑人/行名称
            draft.appendChild(accptrName)
            accptrBank = doc.createElement('accptrBank')
            if line.accptrBank:
                accptrBank.appendChild(doc.createTextNode(line.accptrBank))  # 承兑人所属行号/承兑行号
            draft.appendChild(accptrBank)
            accptrBankName = doc.createElement('accptrBankName')
            if line.accptrBankName:
                accptrBankName.appendChild(doc.createTextNode(line.accptrBankName))  # 承兑人所属行名称/承兑行名
            draft.appendChild(accptrBankName)
            accptrAcctsvcr = doc.createElement('accptrAcctsvcr')
            if line.accptrAcctsvcr:
                accptrAcctsvcr.appendChild(doc.createTextNode(line.accptrAcctsvcr))  # 承兑人/行开户行号
            draft.appendChild(accptrAcctsvcr)
            accptrAcctsvcrName = doc.createElement('accptrAcctsvcrName')
            if line.accptrAcctsvcrName:
                accptrAcctsvcrName.appendChild(doc.createTextNode(line.accptrAcctsvcrName))  # 承兑人/行开户行名
            draft.appendChild(accptrAcctsvcrName)
            accptrAddr = doc.createElement('accptrAddr')
            if line.accptrAddr:
                accptrAddr.appendChild(doc.createTextNode(line.accptrAddr))  # 承兑人/行地址
            draft.appendChild(accptrAddr)
            accptrCtrctNo = doc.createElement('accptrCtrctNo')
            if line.accptrCtrctNo:
                accptrCtrctNo.appendChild(doc.createTextNode(line.accptrCtrctNo))  # 承兑协议编号
            draft.appendChild(accptrCtrctNo)
            txCtrctNb = doc.createElement('txCtrctNb')
            if line.txCtrctNb:
                txCtrctNb.appendChild(doc.createTextNode(line.txCtrctNb))  # 交易合同号
            draft.appendChild(txCtrctNb)
            bnkEndrsmtmk = doc.createElement('bnkEndrsmtmk')
            if line.bnkEndrsmtmk:
                bnkEndrsmtmk.appendChild(doc.createTextNode(line.bnkEndrsmtmk))  # 是否可以转让
            draft.appendChild(bnkEndrsmtmk)
            preHolderName = doc.createElement('preHolderName')
            if line.preHolderName:
                preHolderName.appendChild(doc.createTextNode(line.preHolderName))  # 前手
            draft.appendChild(preHolderName)
            draftSet.appendChild(draft)
        param.appendChild(draftSet)
        paramSet.appendChild(param)
        # 加入到body
        body.appendChild(paramSet)
        # 添加到跟元素中
        efmp.appendChild(body)
        doc.appendChild(efmp)
        return doc.toprettyxml(encoding='utf-8')

    @classmethod
    def package_weekly_funding_plan_to_xml(cls, plan):
        """将付款信息封装成类型为'付款'的xml并返回(70001)
        :param plan: 资金池周计划
        :return string: 资金池周计划xml字符串
        """
        csystem_code = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_code')
        csystem_name = request.env['ir.values'].get_default('interface.bank.settings', 'csystem_name')
        now_time = datetime.datetime.now()

        doc = xml.dom.minidom.Document()
        # 根元素以及属性
        efmp = doc.createElement('efmp')
        efmp.setAttribute('standard', 'FEG')
        efmp.setAttribute('type', '70001')
        efmp.setAttribute('version', '1.0')
        # -----头部信息----
        header = doc.createElement('header')
        appCode = doc.createElement('appCode')
        appCode.appendChild(doc.createTextNode(csystem_code))  # 接入系统代码
        appName = doc.createElement('appName')
        appName.appendChild(doc.createTextNode(csystem_name))  # 接入系统名称
        packageId = doc.createElement('packageId')
        packageId.appendChild(doc.createTextNode(plan.requestId))  # 报文标识号
        createDate = doc.createElement('createDate')
        createDate.appendChild(doc.createTextNode(now_time.strftime('%Y%m%d')))  # 报文日期（yyyyMMdd）
        createTime = doc.createElement('createTime')
        createTime.appendChild(doc.createTextNode(now_time.strftime('%H%M%S')))  # 提交时间（HHmmss）
        header.appendChild(appCode)
        header.appendChild(appName)
        header.appendChild(packageId)
        header.appendChild(createDate)
        header.appendChild(createTime)
        efmp.appendChild(header)
        # ----消息体信息----
        body = doc.createElement('body')
        paramSet = doc.createElement('paramSet')

        # -----每笔付款信息----
        param = doc.createElement('param')
        custNo = doc.createElement('custNo')
        custNo.appendChild(doc.createTextNode(plan.custNo))  # 客户编号
        param.appendChild(custNo)
        custName = doc.createElement('custName')
        custName.appendChild(doc.createTextNode(plan.custName))  # 客户名称
        param.appendChild(custName)
        startDate = doc.createElement('startDate')
        start_date = datetime.datetime.strptime(plan.startDate, '%Y-%m-%d')
        startDate.appendChild(doc.createTextNode(start_date.strftime('%Y%m%d')))  # 开始日期(周一)
        param.appendChild(startDate)
        endDate = doc.createElement('endDate')
        end_date = datetime.datetime.strptime(plan.endDate, '%Y-%m-%d')
        endDate.appendChild(doc.createTextNode(end_date.strftime('%Y%m%d')))  # 开始日期(周日)
        param.appendChild(endDate)

        weekUp = doc.createElement('weekUp')
        weekUp.appendChild(doc.createTextNode(str(plan.weekUp)))  # 周上划资金
        param.appendChild(weekUp)
        weekDown = doc.createElement('weekDown')
        weekDown.appendChild(doc.createTextNode(str(plan.weekDown)))  # 周下拨资金
        param.appendChild(weekDown)
        mondayUp = doc.createElement('mondayUp')
        mondayUp.appendChild(doc.createTextNode(str(plan.mondayUp)))  # 周一上划资金
        param.appendChild(mondayUp)
        mondayDown = doc.createElement('mondayDown')
        mondayDown.appendChild(doc.createTextNode(str(plan.mondayDown)))  # 周一下拨资金
        param.appendChild(mondayDown)
        tuesdayUp = doc.createElement('tuesdayUp')
        tuesdayUp.appendChild(doc.createTextNode(str(plan.tuesdayUp)))  # 周二上划资金
        param.appendChild(tuesdayUp)
        tuesdayDown = doc.createElement('tuesdayDown')
        tuesdayDown.appendChild(doc.createTextNode(str(plan.tuesdayDown)))  # 周二下拨资金
        param.appendChild(tuesdayDown)
        wednesdayUp = doc.createElement('wednesdayUp')
        wednesdayUp.appendChild(doc.createTextNode(str(plan.wednesdayUp)))  # 周三上划资金
        param.appendChild(wednesdayUp)
        wednesdayDown = doc.createElement('wednesdayDown')
        wednesdayDown.appendChild(doc.createTextNode(str(plan.wednesdayDown)))  # 周三下拨资金
        param.appendChild(wednesdayDown)
        thursdayUp = doc.createElement('thursdayUp')
        thursdayUp.appendChild(doc.createTextNode(str(plan.thursdayUp)))  # 周四上划资金
        param.appendChild(thursdayUp)
        thursdayDown = doc.createElement('thursdayDown')
        thursdayDown.appendChild(doc.createTextNode(str(plan.thursdayDown)))  # 周四下拨资金
        param.appendChild(thursdayDown)
        fridayUp = doc.createElement('fridayUp')
        fridayUp.appendChild(doc.createTextNode(str(plan.fridayUp)))  # 周五上划资金
        param.appendChild(fridayUp)
        fridayDown = doc.createElement('fridayDown')
        fridayDown.appendChild(doc.createTextNode(str(plan.fridayDown)))  # 周五下拨资金
        param.appendChild(fridayDown)
        saturdayUp = doc.createElement('saturdayUp')
        saturdayUp.appendChild(doc.createTextNode(str(plan.saturdayUp)))  # 周六上划资金
        param.appendChild(saturdayUp)
        saturdayDown = doc.createElement('saturdayDown')
        saturdayDown.appendChild(doc.createTextNode(str(plan.saturdayDown)))  # 周六下拨资金
        param.appendChild(saturdayDown)
        sundayUp = doc.createElement('sundayUp')
        sundayUp.appendChild(doc.createTextNode(str(plan.sundayUp)))  # 周日上划资金
        param.appendChild(sundayUp)
        sundayDown = doc.createElement('sundayDown')
        sundayDown.appendChild(doc.createTextNode(str(plan.sundayDown)))  # 周日下拨资金
        param.appendChild(sundayDown)
        paramSet.appendChild(param)
        # 加入到body
        body.appendChild(paramSet)
        # 添加到跟元素中
        efmp.appendChild(body)
        doc.appendChild(efmp)
        return doc.toprettyxml(encoding='utf-8')
