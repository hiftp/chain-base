# -*- coding: utf-8 -*-
import datetime
import xml.dom.minidom
import logging
import json
import xmltodict
from pyexpat import ExpatError

from odoo.http import request
import sys

class ControllerFunctions(classmethod):

    @classmethod
    def check_xml_values(cls, str_xml):
        """检查传递的xml的各值是否正确
        :param str_xml:传递的xml
        """
        c_result = {'state': True}
        logging.info(str_xml)
        # 解析xml
        try:
            result_json = json.dumps(xmltodict.parse(str_xml), indent=1, encoding='utf-8')
        except ExpatError:
            return {'state': False, 'result_xml': cls.package_return_xml(u'999', u"xml格式不正确!")}
        result_json = json.loads(result_json.strip())
        payment = result_json['payment']
        system_name = False
        # 检查header
        if not payment.has_key('header'):
            return {'state': False, 'result_xml': cls.package_return_xml(u'null', u"xml格式不正确!")}
        header = payment['header']
        if not header.has_key('system') or not header.has_key('create_time') or not header.has_key('create_date'):
            return {'state': False, 'result_xml': cls.package_return_xml(u'null', u"header中数据不规范(header)!")}
        if not header.get('system'):
            return {'state': False, 'result_xml': cls.package_return_xml(u'null', u"外部系统名称非法!")}
        system_name = header.get('system')
        if not header.get('create_time'):
            return {'state': False, 'result_xml': cls.package_return_xml(system_name, u"create_time非法!")}
        if not header.get('create_date'):
            return {'state': False, 'result_xml': cls.package_return_xml(system_name, u"create_date非法!")}
        try:
            datetime.datetime.strptime(header.get('create_time'), '%H:%M:%S')
        except ValueError:
            return {'state': False, 'result_xml': cls.package_return_xml(system_name, u"create_time格式不规范!")}
        try:
            datetime.datetime.strptime(header.get('create_date'), '%Y-%m-%d')
        except ValueError:
            return {'state': False, 'result_xml': cls.package_return_xml(system_name, u"create_date格式不规范!")}
        # 检查body的from
        body = payment['body']
        form = body['form']
        # 检查必填项
        s_state = cls.check_form_filed(form, system_name)
        if not s_state['state']:
            return {'state': False, 'result_xml': s_state['mes']}
        # 检查单据是否重复
        s_state = cls.check_is_redundant(form, system_name)
        if not s_state['state']:
            return {'state': False, 'result_xml': s_state['result_xml']}
        # 检查单据字段是否正确
        s_state = cls.check_form_values(form, system_name)
        if not s_state['state']:
            return {'state': False, 'result_xml': s_state['result_xml']}
        return c_result

    @classmethod
    def check_is_redundant(cls, form, system_name):
        """检查单据是否已经存在"""
        if isinstance(form, dict):
            payment = request.env['interface.bank.payment'].sudo().search(
                [('source_number', '=', form['source_number']), ('source_model', '=', form['source_model'])])
            if len(payment) >= 1:
                request_data = [{
                    'form_number': form.get('source_number'),
                    'model_name': form['source_model'],
                    'company': form['company_code'],
                    'state_code': '1002',
                    'msg': u"不允许重复传递单据!",
                }]
                return {'state': False, 'result_xml': cls.handling_general_request_messages(system_name, request_data)}
        elif isinstance(form, list):
            request_data = list()
            for f in form:
                payment = request.env['interface.bank.payment'].sudo().search(
                    [('source_number', '=', f['source_number']), ('source_model', '=', f['source_model'])])
                if len(payment) >= 1:
                    data = {
                        'form_number': f.get('source_number'),
                        'model_name': f['source_model'],
                        'company': f['company_code'],
                        'state_code': '1002',
                        'msg': u"不允许重复传递单据!",
                    }
                    request_data.append(data)
            if request_data:
                return {'state': False,
                        'result_xml': cls.handling_general_request_messages(system_name, request_data)}
        return {'state': True}

    @classmethod
    def check_form_filed(cls, form, system_name):
        """检查form单据的必填项"""
        if isinstance(form, dict):
            if not form.has_key('source_number'):
                return {'state': False, 'mes': cls.package_return_xml(system_name, u"source_number(付款单据编号)字段为必填项!")}
            if not form.has_key('source_model'):
                return {'state': False, 'mes': cls.package_return_xml(system_name, u"单据模型(source_model)字段为必填项!")}
            if not form.has_key('company_code'):
                return {'state': False, 'mes': cls.package_return_xml(system_name, u"公司编码(company_code)字段为必填项!")}
            if not form.has_key('currency_type'):
                return {'state': False, 'mes': cls.package_return_xml(system_name, u"币种(currency_type)字段为必填项!")}
            if not form.has_key('partner_id'):
                return {'state': False, 'mes': cls.package_return_xml(system_name, u"收款户名(partner_id)字段为必填项!")}
            if not form.has_key('partner_bank_number'):
                return {'state': False, 'mes': cls.package_return_xml(system_name, u"收款账号字段为必填项!")}
            if not form.has_key('partner_number'):
                return {'state': False, 'mes': cls.package_return_xml(system_name, u"收款人编码字段为必填项!")}
            if not form.has_key('pay_money'):
                return {'state': False, 'mes': cls.package_return_xml(system_name, u"付款金额字段为必填项!")}
        if isinstance(form, list):
            for f in form:
                if not f.has_key('source_number'):
                    return {'state': False, 'mes': cls.package_return_xml(system_name, u"source_number(付款单据编号)字段为必填项!")}
                if not f.has_key('source_model'):
                    return {'state': False, 'mes': cls.package_return_xml(system_name, u"单据模型(source_model)字段为必填项!")}
                if not f.has_key('company_code'):
                    return {'state': False, 'mes': cls.package_return_xml(system_name, u"公司编码(company_code)字段为必填项!")}
                if not f.has_key('currency_type'):
                    return {'state': False, 'mes': cls.package_return_xml(system_name, u"币种(currency_type)字段为必填项!")}
                if not f.has_key('partner_id'):
                    return {'state': False, 'mes': cls.package_return_xml(system_name, u"收款户名(partner_id)字段为必填项!")}
                if not f.has_key('partner_bank_number'):
                    return {'state': False, 'mes': cls.package_return_xml(system_name, u"收款账号字段为必填项!")}
                if not f.has_key('partner_number'):
                    return {'state': False, 'mes': cls.package_return_xml(system_name, u"收款人编码字段为必填项!")}
                if not f.has_key('pay_money'):
                    return {'state': False, 'mes': cls.package_return_xml(system_name, u"付款金额字段为必填项!")}
        return {'state': True}

    @classmethod
    def package_return_xml(cls, system_name, msg):
        """异常处理xml报文"""
        now_time = datetime.datetime.now()
        doc = xml.dom.minidom.Document()
        # 根元素以及属性
        payment = doc.createElement('payment')
        # -----头部信息----
        header = doc.createElement('header')
        system = doc.createElement('system')
        system.appendChild(doc.createTextNode(system_name))  # 接入系统名称
        header.appendChild(system)
        create_date = doc.createElement('create_date')
        create_date.appendChild(doc.createTextNode(now_time.strftime('%Y-%m-%d')))  # 报文日期
        header.appendChild(create_date)
        create_time = doc.createElement('create_time')
        create_time.appendChild(doc.createTextNode(now_time.strftime('%H:%M:%S')))  # 报文时间
        header.appendChild(create_time)
        payment.appendChild(header)
        # ----消息体信息----
        body = doc.createElement('body')
        result = doc.createElement('result')
        state = doc.createElement('state')
        state.appendChild(doc.createTextNode("1001"))  # 状态
        result.appendChild(state)
        message = doc.createElement('message')
        message.appendChild(doc.createTextNode(msg))  # 消息
        result.appendChild(message)
        body.appendChild(result)
        payment.appendChild(body)
        doc.appendChild(payment)
        return doc.toprettyxml(encoding='utf-8')

    @classmethod
    def handling_general_request_messages(cls, system_name, request_data):
        now_time = datetime.datetime.now()
        doc = xml.dom.minidom.Document()
        payment = doc.createElement('payment')
        header = doc.createElement('header')
        system = doc.createElement('system')
        system.appendChild(doc.createTextNode(system_name))  # 接入系统名称
        header.appendChild(system)
        create_date = doc.createElement('create_date')
        create_date.appendChild(doc.createTextNode(now_time.strftime('%Y-%m-%d')))  # 报文日期
        header.appendChild(create_date)
        create_time = doc.createElement('create_time')
        create_time.appendChild(doc.createTextNode(now_time.strftime('%H:%M:%S')))  # 报文时间
        header.appendChild(create_time)
        payment.appendChild(header)
        body = doc.createElement('body')
        for d in request_data:
            result = doc.createElement('result')
            source_number = doc.createElement('source_number')
            source_number.appendChild(doc.createTextNode(d['form_number']))  # 单据编号
            result.appendChild(source_number)
            source_model = doc.createElement('source_model')
            source_model.appendChild(doc.createTextNode(d['model_name']))  # 单据模型
            result.appendChild(source_model)
            company_code = doc.createElement('company_code')
            company_code.appendChild(doc.createTextNode(d['company']))  # 公司编码
            result.appendChild(company_code)
            state = doc.createElement('state')
            state.appendChild(doc.createTextNode(d['state_code']))  # 状态
            result.appendChild(state)
            message = doc.createElement('message')
            message.appendChild(doc.createTextNode(d['msg']))  # 消息
            result.appendChild(message)
            body.appendChild(result)
        payment.appendChild(body)
        doc.appendChild(payment)
        return doc.toprettyxml(encoding='utf-8')

    @classmethod
    def check_form_values(cls, form, system_name):
        """检查传递的单据的值是否正确"""
        if isinstance(form, dict):
            # 公司编码
            company = request.env['res.company'].sudo().search([('code', '=', form['company_code'])])
            if len(company) != 1:
                list_data = cls.create_request_data(form['source_number'], form['source_model'], form['company_code'],
                                                    u"公司编码不正确!")
                return {'state': False, 'result_xml': cls.handling_general_request_messages(system_name, list_data)}
            # 公私标志
            if form.has_key('public_signs'):
                if form.get('public_signs') != '00' and form.get('public_signs') != '01':
                    list_data = cls.create_request_data(form['source_number'], form['source_model'],
                                                        form['company_code'],
                                                        u"公私标识value不正确!")
                    return {'state': False, 'result_xml': cls.handling_general_request_messages(system_name, list_data)}
            # 付款模式
            if form.has_key('payment_model'):
                if form['payment_model'] != '01' and form['payment_model'] != '02':
                    list_data = cls.create_request_data(form['source_number'], form['source_model'],
                                                        form['company_code'],
                                                        u"付款模式value不正确!")
                    return {'state': False, 'result_xml': cls.handling_general_request_messages(system_name, list_data)}
            # 跨行标识
            if form.has_key('cross_row_identi'):
                if form.get('cross_row_identi') != '0' and form.get('cross_row_identi') != '1':
                    list_data = cls.create_request_data(form['source_number'], form['source_model'],
                                                        form['company_code'],
                                                        u"跨行标识value不正确!")
                    return {'state': False, 'result_xml': cls.handling_general_request_messages(system_name, list_data)}
            # 异地标识
            if form.has_key('off_site_identi'):
                if form.get('off_site_identi') != '0' and form.get('off_site_identi') != '1':
                    list_data = cls.create_request_data(form['source_number'], form['source_model'],
                                                        form['company_code'],
                                                        u"异地标识value不正确!")
                    return {'state': False,
                            'result_xml': cls.handling_general_request_messages(system_name, list_data)}
            # 收款方标识
            if form.has_key('payee_identi'):
                if form.get('payee_identi') != '01' and form.get('payee_identi') != '02':
                    list_data = cls.create_request_data(form['source_number'], form['source_model'],
                                                        form['company_code'],
                                                        u"收款方标识value不正确!")
                    return {'state': False,
                            'result_xml': cls.handling_general_request_messages(system_name, list_data)}
            # 借贷标识
            if form.has_key('debit_identi'):
                if form.get('debit_identi') != 'D' and form.get('debit_identi') != 'C':
                    list_data = cls.create_request_data(form['source_number'], form['source_model'],
                                                        form['company_code'],
                                                        u"借贷标识value不正确!")
                    return {'state': False,
                            'result_xml': cls.handling_general_request_messages(system_name, list_data)}
            # 金额
            if form.has_key('pay_money'):
                if not form.get('pay_money').replace('.', '', 1).isdigit():
                    list_data = cls.create_request_data(form['source_number'], form['source_model'],
                                                        form['company_code'],
                                                        u"付款金额value格式不正确!")
                    return {'state': False,
                            'result_xml': cls.handling_general_request_messages(system_name, list_data)}
            # 币种检查
            if not form.get('currency_type'):
                list_data = cls.create_request_data(form['source_number'], form['source_model'],
                                                    form['company_code'],
                                                    u"单据币种字段不正确(currency_type)不正确!")
                return {'state': False,
                        'result_xml': cls.handling_general_request_messages(system_name, list_data)}
            currency_type = request.env['bank.currency'].sudo().search([('code', '=', form['currency_type'])])
            if len(currency_type) < 1:
                list_data = cls.create_request_data(form['source_number'], form['source_model'],
                                                    form['company_code'],
                                                    u"单据币种字段不正确(currency_type)不正确!")
                return {'state': False,
                        'result_xml': cls.handling_general_request_messages(system_name, list_data)}
        if isinstance(form, list):
            for fo in form:
                # 公司编码
                company = request.env['res.company'].sudo().search([('code', '=', fo['company_code'])])
                if len(company) != 1:
                    list_data = cls.create_request_data(fo['source_number'], fo['source_model'],
                                                        fo['company_code'],
                                                        u"公司编码不正确!")
                    return {'state': False, 'result_xml': cls.handling_general_request_messages(system_name, list_data)}
                # 公私标志
                if fo.has_key('public_signs'):
                    if fo.get('public_signs') != '00' and fo.get('public_signs') != '01':
                        list_data = cls.create_request_data(fo['source_number'], fo['source_model'],
                                                            fo['company_code'],
                                                            u"公私标识value不正确!")
                        return {'state': False,
                                'result_xml': cls.handling_general_request_messages(system_name, list_data)}
                # 付款模式
                if fo.has_key('payment_model'):
                    if fo['payment_model'] != '01' and fo['payment_model'] != '02':
                        list_data = cls.create_request_data(fo['source_number'], fo['source_model'],
                                                            fo['company_code'],
                                                            u"付款模式value不正确!")
                        return {'state': False,
                                'result_xml': cls.handling_general_request_messages(system_name, list_data)}
                # 跨行标识
                if fo.has_key('cross_row_identi'):
                    if fo.get('cross_row_identi') != '0' and fo.get('cross_row_identi') != '1':
                        list_data = cls.create_request_data(fo['source_number'], fo['source_model'],
                                                            fo['company_code'],
                                                            u"跨行标识value不正确!")
                        return {'state': False,
                                'result_xml': cls.handling_general_request_messages(system_name, list_data)}
                # 异地标识
                if fo.has_key('off_site_identi'):
                    if fo.get('off_site_identi') != '0' and fo.get('off_site_identi') != '1':
                        list_data = cls.create_request_data(fo['source_number'], fo['source_model'],
                                                            fo['company_code'],
                                                            u"异地标识value不正确!")
                        return {'state': False,
                                'result_xml': cls.handling_general_request_messages(system_name, list_data)}
                # 收款方标识
                if fo.has_key('payee_identi'):
                    if fo.get('payee_identi') != '01' and fo.get('payee_identi') != '02':
                        list_data = cls.create_request_data(fo['source_number'], fo['source_model'],
                                                            fo['company_code'],
                                                            u"收款方标识value不正确!")
                        return {'state': False,
                                'result_xml': cls.handling_general_request_messages(system_name, list_data)}
                # 借贷标识
                if fo.has_key('debit_identi'):
                    if fo.get('debit_identi') != 'D' and fo.get('debit_identi') != 'C':
                        list_data = cls.create_request_data(fo['source_number'], fo['source_model'],
                                                            fo['company_code'],
                                                            u"借贷标识value不正确!")
                        return {'state': False,
                                'result_xml': cls.handling_general_request_messages(system_name, list_data)}
                # 金额
                if fo.has_key('pay_money'):
                    if not fo.get('pay_money').replace('.', '', 1).isdigit():
                        list_data = cls.create_request_data(fo['source_number'], fo['source_model'],
                                                            fo['company_code'],
                                                            u"付款金额value格式不正确!")
                        return {'state': False,
                                'result_xml': cls.handling_general_request_messages(system_name, list_data)}
                # 币种检查
                if not fo.get('currency_type'):
                    list_data = cls.create_request_data(fo['source_number'], fo['source_model'],
                                                        fo['company_code'],
                                                        u"单据币种字段不正确(currency_type)不正确!")
                    return {'state': False,
                            'result_xml': cls.handling_general_request_messages(system_name, list_data)}
                currency_type = request.env['bank.currency'].sudo().search(
                    [('code', '=', fo['currency_type'])])
                if len(currency_type) < 1:
                    list_data = cls.create_request_data(fo['source_number'], fo['source_model'],
                                                        fo['company_code'],
                                                        u"单据币种字段不正确(currency_type)不正确!")
                    return {'state': False,
                            'result_xml': cls.handling_general_request_messages(system_name, list_data)}
        return {'state': True}

    @classmethod
    def create_request_data(cls, source_number, source_model, company_code, msg):
        data = [{
            'form_number': source_number,
            'model_name': source_model,
            'company': company_code,
            'state_code': 'F001',
            'msg': msg,
        }]
        return data

    @classmethod
    def create_payment(cls, str_xml):
        """生成银行付款单"""
        result_json = json.dumps(xmltodict.parse(str_xml), indent=1, encoding='utf-8')
        result_json = json.loads(result_json.strip())
        payment = result_json['payment']
        body = payment['body']
        form = body['form']
        if isinstance(form, dict):
            company = request.env['res.company'].sudo().search([('code', '=', form['company_code'])])
            payee_bank = False
            try:
                payee_bank = form['payee_bank']
            except KeyError:
                payee_bank = ''
            try:
                payee_bank_code = form['payee_bank_code']
            except KeyError:
                payee_bank_code = ''
            try:
                payee_opening_bank = form['payee_opening_bank']
            except KeyError:
                payee_opening_bank = ''
            try:
                payee_opening_bank_code = form['payee_opening_bank_code']
            except KeyError:
                payee_opening_bank_code = ''
            try:
                payee_opening_province = form['payee_opening_province']
            except KeyError:
                payee_opening_province = ''
            try:
                payee_opening_province_code = form['payee_opening_province_code']
            except KeyError:
                payee_opening_province_code = ''
            try:
                payee_opening_city = form['payee_opening_city']
            except KeyError:
                payee_opening_city = ''
            try:
                payee_opening_city_code = form['payee_opening_city_code']
            except KeyError:
                payee_opening_city_code = ''
            currency_type = request.env['bank.currency'].sudo().search([('code', '=', form['currency_type'])])
            # 判断联系人等是否存在
            try:
                partner_contact_phone = form['partner_contact_phone']
            except KeyError:
                partner_contact_phone = ''
            try:
                partner_contact_add = form['partner_contact_add']
            except KeyError:
                partner_contact_add = ''
            try:
                pay_summary = form['pay_summary']
            except KeyError:
                pay_summary = ''
            try:
                pay_use = form['pay_use']
            except KeyError:
                pay_use = ''
            request.env['interface.bank.payment'].sudo().create({
                'public_signs': form['public_signs'],
                'payment_model': form['payment_model'],
                'source_number': form['source_number'],
                'source_model': form['source_model'],
                'company_id': company[0].id,
                'cross_row_identi': form['cross_row_identi'],
                'off_site_identi': form['off_site_identi'],
                'payee_identi': form['payee_identi'],
                'debit_identi': form['debit_identi'],
                'payee_bank': payee_bank,
                'payee_bank_code': payee_bank_code,
                'payee_opening_bank': payee_opening_bank,
                'payee_opening_bank_code': payee_opening_bank_code,
                'payee_opening_province': payee_opening_province,
                'payee_opening_province_code': payee_opening_province_code,
                'payee_opening_city': payee_opening_city,
                'payee_opening_city_code': payee_opening_city_code,
                'currency_type': currency_type[0].id,
                'partner_id': form['partner_id'],
                'partner_bank_number': form['partner_bank_number'],
                'partner_number': form['partner_number'],
                'partner_contact': form['partner_contact'],
                'partner_contact_phone': partner_contact_phone,
                'partner_contact_add': partner_contact_add,
                'pay_money': form['pay_money'],
                'pay_summary': pay_summary,
                'pay_use': pay_use,
                'form_code': '',
                'external_system_from': 'y',
            })
            request_data = [{
                'form_number': form.get('source_number'),
                'model_name': form['source_model'],
                'company': form['company_code'],
                'state_code': '0000',
                'msg': u"财务系统已成功接收单据!",
            }]
            header = payment['header']
            system_name = header.get('system')
            return {'state': True, 'result_xml': cls.handling_general_request_messages(system_name, request_data)}
        if isinstance(form, list):
            request_list = list()
            for f in form:
                try:
                    payee_bank = f['payee_bank']
                except KeyError:
                    payee_bank = ''
                try:
                    payee_bank_code = f['payee_bank_code']
                except KeyError:
                    payee_bank_code = ''
                try:
                    payee_opening_bank = f['payee_opening_bank']
                except KeyError:
                    payee_opening_bank = ''
                try:
                    payee_opening_bank_code = f['payee_opening_bank_code']
                except KeyError:
                    payee_opening_bank_code = ''
                try:
                    payee_opening_province = f['payee_opening_province']
                except KeyError:
                    payee_opening_province = ''
                try:
                    payee_opening_province_code = f['payee_opening_province_code']
                except KeyError:
                    payee_opening_province_code = ''
                try:
                    payee_opening_city = f['payee_opening_city']
                except KeyError:
                    payee_opening_city = ''
                try:
                    payee_opening_city_code = f['payee_opening_city_code']
                except KeyError:
                    payee_opening_city_code = ''
                company = request.env['res.company'].sudo().search([('code', '=', f['company_code'])])
                currency_type = request.env['bank.currency'].sudo().search([('code', '=', f['currency_type'])])
                try:
                    partner_contact_phone = f['partner_contact_phone']
                except KeyError:
                    partner_contact_phone = ''
                try:
                    partner_contact_add = f['partner_contact_add']
                except KeyError:
                    partner_contact_add = ''
                try:
                    pay_summary = f['pay_summary']
                except KeyError:
                    pay_summary = ''
                try:
                    pay_use = f['pay_use']
                except KeyError:
                    pay_use = ''
                request.env['interface.bank.payment'].sudo().create({
                    'public_signs': f['public_signs'],
                    'payment_model': f['payment_model'],
                    'source_number': f['source_number'],
                    'source_model': f['source_model'],
                    'company_id': company[0].id,
                    'cross_row_identi': f['cross_row_identi'],
                    'off_site_identi': f['off_site_identi'],
                    'payee_identi': f['payee_identi'],
                    'debit_identi': f['debit_identi'],
                    'payee_bank': payee_bank,
                    'payee_bank_code': payee_bank_code,
                    'payee_opening_bank': payee_opening_bank,
                    'payee_opening_bank_code': payee_opening_bank_code,
                    'payee_opening_province': payee_opening_province,
                    'payee_opening_province_code': payee_opening_province_code,
                    'payee_opening_city': payee_opening_city,
                    'payee_opening_city_code': payee_opening_city_code,
                    'currency_type': currency_type[0].id,
                    'partner_id': f['partner_id'],
                    'partner_bank_number': f['partner_bank_number'],
                    'partner_number': f['partner_number'],
                    'partner_contact': f['partner_contact'],
                    'partner_contact_phone': partner_contact_phone,
                    'partner_contact_add': partner_contact_add,
                    'pay_money': f['pay_money'],
                    'pay_summary': pay_summary,
                    'pay_use': pay_use,
                    'form_code': '',
                    'external_system_from': 'y',
                })
                data = {
                    'form_number': f['source_number'],
                    'model_name': f['source_model'],
                    'company': f['company_code'],
                    'state_code': '0000',
                    'msg': u"财务系统已成功接收单据!",
                }
                request_list.append(data)
            header = payment['header']
            system_name = header.get('system')
            return {'state': True, 'result_xml': cls.handling_general_request_messages(system_name, request_list)}

    @classmethod
    def check_search_xml(cls, str_xml):
        """检查查询付款单据xml格式和数据结构"""
        c_result = {'state': True}
        logging.info(str_xml)
        # 解析xml
        result_json = json.dumps(xmltodict.parse(str_xml), indent=1, encoding='utf-8')
        result_json = json.loads(result_json.strip())
        try:
            payment = result_json['payment']
            header = payment['header']
            body = payment['body']
            form = body['form']
            c_result['form'] = form
        except KeyError:
            return {'state': False, 'result_xml': cls.package_return_xml(u'101', u"XML结构异常,请检查XML数据!")}
        except TypeError:
            return {'state': False, 'result_xml': cls.package_return_xml(u'101', u"XML结构异常,请检查XML数据!")}
        # 检查header
        if not payment.has_key('header'):
            return {'state': False, 'result_xml': cls.package_return_xml(u'null', u"xml格式不正确!")}
        if not header.has_key('system') or not header.has_key('create_time') or not header.has_key('create_date'):
            return {'state': False, 'result_xml': cls.package_return_xml(u'null', u"header中数据不规范(header)!")}
        if not header.get('system'):
            return {'state': False, 'result_xml': cls.package_return_xml(u'null', u"外部系统名称非法!")}
        system_name = header.get('system')
        c_result['system_name'] = system_name
        if not header.get('create_time'):
            return {'state': False, 'result_xml': cls.package_return_xml(system_name, u"create_time非法!")}
        if not header.get('create_date'):
            return {'state': False, 'result_xml': cls.package_return_xml(system_name, u"create_date非法!")}
        try:
            datetime.datetime.strptime(header.get('create_time'), '%H:%M:%S')
        except ValueError:
            return {'state': False, 'result_xml': cls.package_return_xml(system_name, u"create_time格式不规范!")}
        try:
            datetime.datetime.strptime(header.get('create_date'), '%Y-%m-%d')
        except ValueError:
            return {'state': False, 'result_xml': cls.package_return_xml(system_name, u"create_date格式不规范!")}
        # 检查body的from
        if isinstance(form, dict):
            if not form.has_key('form_number'):
                return {'state': False, 'result_xml': cls.package_return_xml(system_name, u"未发现form_number属性和值（单据编号）!")}
            if not form.has_key('form_model'):
                return {'state': False, 'result_xml': cls.package_return_xml(system_name, u"未发现form_model属性和值（单据模型）!")}
            if not form.get('form_number'):
                return {'state': False, 'result_xml': cls.package_return_xml(system_name, u"form_number（单据编号）值异常!")}
            if not form.get('form_model'):
                return {'state': False, 'result_xml': cls.package_return_xml(system_name, u"form_model（单据模型）值异常!")}
        if isinstance(form, list):
            for f in form:
                if not f.has_key('form_number'):
                    return {'state': False,
                            'result_xml': cls.package_return_xml(system_name, u"未发现form_number属性和值（单据编号）!")}
                if not f.has_key('form_model'):
                    return {'state': False,
                            'result_xml': cls.package_return_xml(system_name, u"未发现form_model属性和值（单据模型）!")}
                if not f.get('form_number'):
                    return {'state': False, 'result_xml': cls.package_return_xml(system_name, u"form_number（单据编号）值异常!")}
                if not f.get('form_model'):
                    return {'state': False, 'result_xml': cls.package_return_xml(system_name, u"form_model（单据模型）值异常!")}
        return c_result

    @classmethod
    def search_payment_state(cls, search_data):
        """返回查询结果的list集合"""
        result_list = list()
        if isinstance(search_data, dict):
            data = {'form_number': search_data['form_number'], 'form_model': search_data['form_model']}
            payment = request.env['interface.bank.payment'].sudo().search(
                [('source_number', '=', search_data['form_number']), ('source_model', '=', search_data['form_model'])])
            if len(payment) < 1:
                data['payment_state'] = 'F001'
            elif len(payment) >= 1:
                data['payment_state'] = payment[0].state
                data['company_code'] = payment[0].company_id.code
                data['company_name'] = payment[0].company_id.name
            else:
                data['payment_state'] = '999'
            result_list.append(data)
        if isinstance(search_data, list):
            for s_data in search_data:
                data = {'form_number': s_data['form_number'], 'form_model': s_data['form_model']}
                payment = request.env['interface.bank.payment'].sudo().search(
                    [('source_number', '=', s_data['form_number']),
                     ('source_model', '=', s_data['form_model'])])
                if len(payment) < 1:
                    data['payment_state'] = 'F001'
                elif len(payment) >= 1:
                    data['payment_state'] = payment[0].state
                    data['company_code'] = payment[0].company_id.code
                    data['company_name'] = payment[0].company_id.name
                else:
                    data['payment_state'] = '999'
                result_list.append(data)
        return result_list

    @classmethod
    def package_search_result_xml(cls, system_name, result_list):
        """返回查询结果xml"""
        now_time = datetime.datetime.now()
        doc = xml.dom.minidom.Document()
        payment = doc.createElement('payment')
        header = doc.createElement('header')
        system = doc.createElement('system')
        system.appendChild(doc.createTextNode(system_name))  # 接入系统名称
        header.appendChild(system)
        create_date = doc.createElement('create_date')
        create_date.appendChild(doc.createTextNode(now_time.strftime('%Y-%m-%d')))  # 报文日期
        header.appendChild(create_date)
        create_time = doc.createElement('create_time')
        create_time.appendChild(doc.createTextNode(now_time.strftime('%H:%M:%S')))  # 报文时间
        header.appendChild(create_time)
        state = doc.createElement('state')
        state.appendChild(doc.createTextNode('0000'))  # 状态码
        header.appendChild(state)
        message = doc.createElement('message')
        message.appendChild(doc.createTextNode(u"已成功执行查询操作！"))  # 状态消息
        header.appendChild(message)
        payment.appendChild(header)
        body = doc.createElement('body')
        for res in result_list:
            result = doc.createElement('result')
            form_number = doc.createElement('form_number')
            form_number.appendChild(doc.createTextNode(res['form_number']))  # 单据编号
            result.appendChild(form_number)
            form_model = doc.createElement('form_model')
            form_model.appendChild(doc.createTextNode(res['form_model']))  # 单据模型
            result.appendChild(form_model)
            payment_state = doc.createElement('payment_state')
            payment_state.appendChild(doc.createTextNode(res['payment_state']))  # 付款状态
            result.appendChild(payment_state)
            body.appendChild(result)
        payment.appendChild(body)
        doc.appendChild(payment)
        return doc.toprettyxml(encoding='utf-8')
