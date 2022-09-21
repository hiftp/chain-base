# -*- coding: utf-8 -*-

import datetime
import json
import logging
from odoo.http import Controller, route, request
from functions import ControllerFunctions as cf

logger = logging.getLogger(__name__)


class Payment(Controller):
    """银行付款单外部接口"""

    @route('/interface/bank/create/payment', type='json', auth='none', methods=['get', 'post'], csrf=False)
    def bank_create_payment(self):
        """
        外部系统传递付款单至erp系统外部接口；数据格式为json
        json格式为：   (payments部分支持多条记录传递， 可为dict或list)
        json_data = {
        "system_name": "接入系统名称",
        "system_code": "接入系统代码",
        "create_date": "上传日期yyyy-MM-dd<",
        "create_time": "上传时间HH:mm:ss",
        "payments": [
            {
            "source_number":"付款单据编号",
            "source_model":"单据模型",
            "company_code":"公司编码",
            "public_signs":"公私标识",
            "payment_model":"付款模式",
            "cross_row_identi":"跨行标识",
            "off_site_identi":"异地标识",
            "payee_identi":"收款方标识",
            "debit_identi":"借贷标识",
            "payee_bank":"收款方归属银行名称",
            "payee_bank_code":"收款方归属银行代码",
            "payee_opening_bank":"收款方开户行名称",
            "payee_opening_bank_code":"收款方开户行代码",
            "payee_opening_province":"收款方省份名称",
            "payee_opening_province":"收款方省份名称",
            "abc_provincial_code":"收款方省份代码（农行",
            "payee_opening_city":"收款方城市名称",
            "payee_opening_city_code":"收款方城市代码",
            "abc_city_code":"收款方城市代码（农行）",
            "currency_type":"币种",
            "partner_id":"收款户名",
            "partner_bank_number":"收款账号",
            "partner_number":"客户编号",
            "partner_contact":"收款联系人",
            "partner_contact_phone":"联系人电话",
            "partner_contact_add":"联系人地址",
            "pay_money":"付款金额",
            "pay_summary":"摘要",
            "pay_use":"付款用途",
            }
        ]
        }
        :return: {"state": "状态码", "message":"状态消息"}
        """
        # 检查配置项是否允许传递
        logging.info(u"外部系统正在传递银行付款单...")
        open_interface = request.env['ir.values'].get_default('interface.bank.settings', 'open_interface')
        if open_interface != 'y':
            return json.dumps(self.create_result_json_data(state='1010', message=u"财务ERP系统已设置不允许上传付款单据"),
                              ensure_ascii=False)
        json_str = request.jsonrequest
        if not json_str:
            return json.dumps(self.create_result_json_data(state='1001', message=u"未接收到任何JSON数据"), ensure_ascii=False)
        try:
            logging.info("interface/bank/create/payment-json:{}".format(json_str))
            # 获取传入日期和时间
            datetime.datetime.strptime(json_str.get('create_time'), '%H:%M:%S')
            datetime.datetime.strptime(json_str.get('create_date'), '%Y-%m-%d')
            # 检查单据是否重复
            logging.info(u"检查单据是否重复..")
            result = self.check_is_redundant(json_str['payments'])
            if not result['state']:
                return json.dumps(self.create_result_json_data(state='1002', message=result['message']),
                                  ensure_ascii=False)
            # 检查单据字段是否正确
            logging.info(u"检查单据字段是否正确..")
            result = self.check_form_values(json_str['payments'])
            if not result['state']:
                return json.dumps(self.create_result_json_data(state='1003', message=result['message']),
                                  ensure_ascii=False)
            # 写入付款单
            logging.info(u"写入付款单..")
            payment_len = self.create_payment_by_data(json_str)
            msg = u"ERP已接受'{}'条记录".format(payment_len)
            return json.dumps(self.create_result_json_data(state='0000', message=msg), ensure_ascii=False)
        except KeyError as e:
            msg = u"KeyError:字段'{}'不存在!".format(e.message)
            logging.info(msg)
            return json.dumps(self.create_result_json_data(state='1012', message=msg), ensure_ascii=False)
        except ValueError as e:
            msg = u"ValueError:'{}'".format(e.message)
            logging.info(msg)
            return json.dumps(self.create_result_json_data(state='1013', message=msg), ensure_ascii=False)
        except Exception as e:
            msg = u"Exception:'{}'".format(e.message)
            logging.info(msg)
            return json.dumps(self.create_result_json_data(state='999', message=msg), ensure_ascii=False)

    @route('/interface/bank/search/payment/state', type='json', auth='none', methods=['get', 'post'], csrf=False)
    def search_bank_state(self):
        """
        外部系统查询已传递的付款单支付状态接口；数据格式为json
        json格式为：   (payments部分支持多条记录传递， 可为dict或list)
        json_data = {
        "system_name": "接入系统名称",
        "system_code": "接入系统代码",
        "create_date": "上传日期yyyy-MM-dd<",
        "create_time": "上传时间HH:mm:ss",
        "payment": [
            {
                "form_number": "单据编号",
                "form_model": "单据模型",
            },
            {
                "form_number": "单据编号",
                "form_model": "单据模型",
            }
        ]
        }
        :return: result_json = {
         "state": "状态码",
         "message":"状态消息",
         "results":
             [
                {
                    "form_number": "单据编号",
                    "form_model": "单据模型"
                    "company_code": "公司代码"
                    "payment_state": "付款状态"
                },
                {
                    "form_number": "单据编号",
                    "form_model": "单据模型"
                    "company_code": "公司代码"
                    "payment_state": "付款状态"
                }
             ]
         }
        """
        # 检查配置项是否允许查询
        logging.info(u"外部系统正在查询付款单据状态...")
        search_payment = request.env['ir.values'].get_default('interface.bank.settings', 'search_payment')
        if search_payment != 'y':
            return json.dumps(self.create_result_json_data(state='1010', message=u"财务ERP系统已设置不允许查询单据状态"),
                              ensure_ascii=False)
        json_str = request.jsonrequest
        if not json_str:
            return json.dumps(self.create_result_json_data(state='1001', message=u"未接收到任何要查询的单据数据"), ensure_ascii=False)
        # 执行查询动作
        try:
            logging.info('json_str:{}'.format(json_str))
            results = self.search_patment_state_by_data(json_str)
            msg = u"查询成功"
            return json.dumps({'state': '0000', 'message': msg, 'results': results}, ensure_ascii=False)
        except KeyError as e:
            msg = u"KeyError:字段'{}'不存在!".format(e.message)
            logging.info(msg)
            return json.dumps(self.create_result_json_data(state='1012', message=msg), ensure_ascii=False)
        except ValueError as e:
            msg = u"ValueError:'{}'".format(e.message)
            logging.info(msg)
            return json.dumps(self.create_result_json_data(state='1013', message=msg), ensure_ascii=False)
        except Exception as e:
            msg = u"Exception:'{}'".format(e.message)
            logging.info(msg)
            return json.dumps(self.create_result_json_data(state='999', message=msg), ensure_ascii=False)

    @route('/interface/bank/payment', type='http', auth='none', methods=['get', 'post'], csrf=False)
    def accept_payment(self, **kw):
        """接受外部系统传递付款单"""
        logging.info(u"开始传递银行付款单...")
        # 检查配置项是否允许传递
        open_interface = request.env['ir.values'].get_default('interface.bank.settings', 'open_interface')
        if open_interface != 'y':
            return cf.package_return_xml(u'1010', u"财务ERP系统已设置不允许上传付款单据!")
        str_xml = request.httprequest.data
        if not str_xml:
            return cf.package_return_xml(u'1001', u"未获取到传递的单据信息!")
        c_result = cf.check_xml_values(str_xml)
        if not c_result['state']:
            logging.info(c_result['result_xml'])
            return c_result['result_xml']
        c_result = cf.create_payment(str_xml)
        if c_result['state']:
            logging.info(c_result['result_xml'])
            logging.info(u"结束传递银行付款单...")
            return c_result['result_xml']
        else:
            return cf.package_return_xml(u'999', u"上传出现未知错误!")

    @route('/interface/bank/search/payment', type='http', auth='none', methods=['get', 'post'], csrf=False)
    def search_bank_payment_state(self, **kw):
        """查询付款单付款状态外部接口"""
        logging.info(u"检测到外部系统正在请求查询付款单据状态接口")
        search_payment = request.env['ir.values'].get_default('interface.bank.settings', 'search_payment')
        if search_payment != 'y':
            return cf.package_return_xml(u'1010', u"财务ERP系统已设置不允许查询单据状态!")
        str_xml = request.httprequest.data
        if not str_xml:
            return cf.package_return_xml(u'1001', u"请正确传递查询信息!")
        # 检查xml结构
        c_result = cf.check_search_xml(str_xml)
        if not c_result['state']:
            logging.info(c_result['result_xml'])
            return c_result['result_xml']
        # 执行查询动作
        result_list = cf.search_payment_state(c_result['form'])
        logging.info(u"结束请求查询付款单据状态接口")
        return cf.package_search_result_xml(c_result['system_name'], result_list)

    @classmethod
    def create_result_json_data(cls, source_number=None, source_model=None, company_code=None, state=None,
                                message=None):
        """
        创建返回结果dict数据
        :param source_number: 单据编码
        :param source_model:  单据模型
        :param company_code:  公司代码
        :param state:         状态码
        :param message:       消息
        :return:  dict 返回dict
        """
        result_data = {
            "source_number": source_number if source_number else '',
            "source_model": source_model if source_model else '',
            "company_code": company_code if company_code else '',
            "state": state if state else '999',
            "message": message if message else u'上传出现未知错误',
        }
        logging.info("state:'{}',message:'{}'".format(state, message))
        return result_data

    @classmethod
    def check_is_redundant(cls, data):
        """检查单据是否重复"""
        if isinstance(data, dict):
            payment = request.env['interface.bank.payment'].sudo().search(
                [('source_number', '=', data['source_number']), ('source_model', '=', data['source_model'])])
            if len(payment) >= 1:
                # if payment[0].state != '03':
                # 修改单据传递逻辑，当状态为03交易失败或者04分期付款时可再次传递
                # @author: fengjiqiang@inspur.com
                if payment[0].state not in ['03', '04']:
                # end
                    return {'state': False,
                            'message': u"单据:'{}',模型:'{}'已存在,请不要重复传递!".format(data['source_number'],
                                                                             data['source_model'])}
        elif isinstance(data, list):
            for f in data:
                payment = request.env['interface.bank.payment'].sudo().search(
                    [('source_number', '=', f['source_number']), ('source_model', '=', f['source_model'])])
                if len(payment) >= 1:
                    # if payment[0].state != '03':
                    # 修改单据传递逻辑，当状态为03交易失败或者04分期付款时可再次传递
                    # @author: fengjiqiang@inspur.com
                    if payment[0].state not in ['03', '04']:
                    # end
                        return {'state': False,
                                'message': u"单据:'{}',模型:'{}'已存在,请不要重复传递!".format(f['source_number'], f['source_model'])}
        return {'state': True}

    @classmethod
    def check_form_values(cls, data):
        """检查单据的值是否正确"""
        if isinstance(data, dict):
            return cls.check_form_values_line(data)
        elif isinstance(data, list):
            for d in data:
                res = cls.check_form_values_line(d)
                if not res.get('state'):
                    return res
                return {'state': True}

    @classmethod
    def check_form_values_line(cls, data):
        # 公司编码
        company = request.env['res.company'].sudo().search([('code', '=', data['company_code'])])
        if len(company) < 1:
            return {'state': False, 'message': u"公司编码'{}'不正确!".format(data['company_code'])}
        # 公私标志
        if data.get('public_signs') != '00' and data.get('public_signs') != '01':
            return {'state': False, 'message': u"公私标识'{}'值不正确".format(data.get('public_signs'))}
        # 付款模式
        if data['payment_model'] != '01' and data['payment_model'] != '02':
            return {'state': False, 'message': u"付款模式'{}'值不正确".format(data.get('payment_model'))}
        # 跨行标识
        if data.get('cross_row_identi') != '0' and data.get('cross_row_identi') != '1':
            return {'state': False, 'message': u"跨行标识'{}'值不正确".format(data.get('cross_row_identi'))}
        # 异地标识
        if data.get('off_site_identi') != '0' and data.get('off_site_identi') != '1':
            return {'state': False, 'message': u"异地标识'{}'值不正确".format(data.get('off_site_identi'))}
        # 收款方标识
        if data.get('payee_identi') != '01' and data.get('payee_identi') != '02':
            return {'state': False, 'message': u"收款方标识'{}'值不正确".format(data.get('payee_identi'))}
        # 借贷标识
        if data.get('debit_identi') != 'D' and data.get('debit_identi') != 'C':
            return {'state': False, 'message': u"借贷标识'{}'值不正确".format(data.get('debit_identi'))}
        # 金额
        if not isinstance(data.get('pay_money'), (int, float)):
            if not data.get('pay_money').replace('.', '', 1).isdigit():
                return {'state': False, 'message': u"付款金额'{}'格式不正确".format(data.get('pay_money'))}
        if isinstance(data.get('pay_money'), (int, float)):
            if data.get('pay_money') == 0:
                return {'state': False, 'message': u"付款金额不能为0"}
        # 币种检查
        currency_type = request.env['bank.currency'].sudo().search([('code', '=', data['currency_type'])])
        if len(currency_type) < 1:
            return {'state': False, 'message': u"币种字段不正确'{}'不正确!".format(data['currency_type'])}
        return {'state': True}

    @classmethod
    def create_payment_by_data(cls, data):
        """根据data值创建付款单"""
        payment_len = 1
        payments = data.get('payments')
        if isinstance(payments, dict):
            cls.create_payment_by_data_line(payments)
        if isinstance(payments, list):
            payment_len = len(payments)
            for payment in payments:
                cls.create_payment_by_data_line(payment)
        return payment_len

    @classmethod
    def create_payment_by_data_line(cls, data):
        """创建付款单"""
        # 根据单据编号和模型查询是否已存在，存在则修改，不存在则新增
        payment = request.env['interface.bank.payment'].sudo().search(
            [('source_number', '=', data['source_number']), ('source_model', '=', data['source_model'])])
        if len(payment) >= 1:
            pay_data = cls.pack_payment_data(data)
            pay_data.update({'state': 'approval', 'form_code': payment[0].form_code})
            payment.sudo().write(pay_data)
            msg = u"{}-已重新传递付款信息".format(datetime.datetime.now())
            payment.sudo().message_post(body=msg, message_type='notification')
        else:
            request.env['interface.bank.payment'].sudo().create(cls.pack_payment_data(data))

    @classmethod
    def pack_payment_data(cls, data):
        """创建付款单data并返回"""
        company = request.env['res.company'].sudo().search([('code', '=', data.get('company_code'))])
        currency = request.env['bank.currency'].sudo().search([('code', '=', data['currency_type'])])
        # 增加上传支付记录明细2019-09-05
        # @author: fengjiqiang@inspur.com
        # payment_line_sets = []
        # unpaied_id = request.env['oa.interface.bank.line'].sudo().search([('state', '=', 'unpaied')])
        # for line in unpaied_id:
        #     record = {
        #         "pay_per_money": line.pay_per_money,
        #     }
        #     payment_line_sets.append((0, 0, record))
        # end
        return {
            'public_signs': data['public_signs'],  # 公私标识
            'payment_model': data['payment_model'],  # 付款模式
            'source_number': data['source_number'],  # 来源单据编号
            'source_model': data['source_model'],  # 来源单据模型
            'company_id': company[0].id,  # 公司
            'cross_row_identi': data['cross_row_identi'],  # 跨行标识
            'off_site_identi': data['off_site_identi'],  # 异地标识
            'payee_identi': data['payee_identi'],  # 收款方标识
            'debit_identi': data['debit_identi'],  # 借贷标识
            'payee_bank': data.get('payee_bank') if data.get('payee_bank') else '',  # 收款方归属银行名称
            'payee_bank_code': data.get('payee_bank_code') if data.get('payee_bank_code') else '',  # 收款方归属银行代码
            'payee_opening_bank': data.get('payee_opening_bank') if data.get('payee_opening_bank') else '',  # 收款方开户行名称
            'payee_opening_bank_code': data.get('payee_opening_bank_code') if data.get(
                'payee_opening_bank_code') else '',  # 收款方开户行代码
            'payee_opening_province': data.get('payee_opening_province') if data.get('payee_opening_province') else '',
            # 收款方省份名称
            'payee_opening_province_code': data.get('payee_opening_province_code') if data.get(
                'payee_opening_province_code') else '',  # 收款方省份代码
            'payee_opening_city': data.get('payee_opening_city') if data.get('payee_opening_city') else '',  # 收款方城市名称
            'payee_opening_city_code': data.get('payee_opening_city_code') if data.get(
                'payee_opening_city_code') else '',  # 收款方城市代码
            'abc_provincial_code': data.get('abc_provincial_code'),  # 收款方省份代码(农行)
            'abc_city_code': data.get('abc_city_code'),  # 收款方城市代码(农行)
            'currency_type': currency[0].id if currency else 1,  # 交易币种
            'partner_id': data['partner_id'],  # 收款户名
            'partner_bank_number': data['partner_bank_number'],  # 收款账号
            'partner_number': data['partner_number'],  # 客户编号
            'partner_contact': data['partner_contact'],  # 收款联系人
            'partner_contact_phone': data['partner_contact_phone'],  # 收款联系人电话
            'partner_contact_add': data['partner_contact_add'],  # 收款联系人地址
            'pay_money': data['pay_money'],  # 收款金额
            'pay_summary': data['pay_summary'],  # 摘要
            'pay_use': data['pay_use'] if data['pay_use'] else '',  # 付款用途
            'form_code': '',  #
            'external_system_from': 'y',  # 外部系统传入
            'save_datetime': datetime.datetime.now(),  # 外部系统传入
            # 支付记录
            # @author: fengjiqiang@inspur.com
            'payment_line_ids': data['payment_line_ids'],
            # end
        }

    @classmethod
    def search_patment_state_by_data(cls, data):
        payments = data.get('payment')
        result_list = list()
        if isinstance(payments, dict):
            result_list.append(cls.search_patment_state_by_data_line(payments))
        if isinstance(payments, list):
            for payment in payments:
                result_list.append(cls.search_patment_state_by_data_line(payment))
        return result_list

    @classmethod
    def search_patment_state_by_data_line(cls, data):
        payment = request.env['interface.bank.payment'].sudo().search(
            [('source_number', '=', data['form_number']), ('source_model', '=', data['form_model'])])
        result = {
            'form_number': data['form_number'],
            'form_model': data['form_model'],
        }
        if len(payment) < 1:
            result.update({'payment_state': 'F001', 'company_code': 'null'})
        elif len(payment) >= 1:
            result.update({'payment_state': payment[0].state, 'company_code': payment[0].company_id.code})
        else:
            data['payment_state'] = '999'
        return result
