# -*- coding: utf-8 -*-
import json
import logging
import xml.dom.minidom
from odoo import api, models
from cqt_functions import CqtFunction as cqt
import datetime

_logger = logging.getLogger(__name__)


class BankAutomateTasks(models.TransientModel):
    _name = 'interface.bank.automate.tasks'
    _description = u"银企直联相关自动任务"

    @api.multi
    def automate_update_payment_state(self):
        """自动更新银行付款单状态
        1.获取所有状态为银行确认的付款单
        2.将获取到的付款单编码进行xml封装并发送到银行
        3.解析银行返回的结果
        4.根据结果对相应的单据做单据操作
        """
        logging.info(u"开始定时拉取银行付款状态自动任务...")
        # 通过财企通付款的的单据
        search_sql = """SELECT array_agg(form_code) FROM interface_bank_payment WHERE state='01' AND payment_type='0' OR payment_type='1' OR payment_type='2' """
        logging.info(search_sql)
        cr = self.env.cr
        cr.execute(search_sql)
        rel_results = cr.fetchall()
        for rel in rel_results:
            if not rel[0]:
                break
            logging.info(rel[0])
            xml_str = self.serach_payment_result(rel[0])
            logging.info(xml_str)
            service_url = self.env['ir.values'].get_default('interface.bank.settings', 'feg_add')
            result_xml = cqt.send_xml_to_cqtbankservice(xml_str, service_url)
            result_json = cqt.xml_to_json(result_xml)
            result_json = json.loads(result_json.strip())
            efmp = result_json['efmp']
            body = efmp['body']
            result_set = body['resultSet']
            result = result_set['result']
            if isinstance(result, dict):
                msg = u"""查询单据结果-结果代码:%s,结果说明: %s""" % (result['resultCode'], result['resultMsg'])
                try:
                    # 判断指令状态
                    if result['cmdStatus'] == '12':
                        msg = u"""单据%s,付款状态为（正在处理中),返回消息为:%s""" % (result['requestId'], result['resultMsg'])
                        self.alter_payment_state(form_code=result['requestId'], state=result['cmdStatus'], msg=msg)
                    elif result['cmdStatus'] == '14':
                        msg = u"""单据%s,付款状态为（处理成功),返回消息为:%s""" % (result['requestId'], result['resultMsg'])
                        self.alter_payment_state(form_code=result['requestId'], state=result['cmdStatus'], msg=msg)
                    elif result['cmdStatus'] == '15':
                        msg = u"""单据%s,付款状态为（处理失败),返回消息为:%s""" % (result['requestId'], result['resultMsg'])
                        self.alter_payment_state(form_code=result['requestId'], state=result['cmdStatus'], msg=msg)
                    else:
                        msg = u"""自动任务: 单据%s,付款状态为（指令不存在 或 已收到未处理),返回消息为:%s""" % (
                            result['requestId'], result['resultMsg'])
                        self.alter_payment_state(form_code=result['requestId'], state=result['cmdStatus'], msg=msg)
                    logging.info(msg)
                    self.create_interface_bank_payment_log(result['requestId'], msg)
                except KeyError:
                    logging.info(msg)
                    self.create_interface_bank_payment_log(result['requestId'], msg)
            if isinstance(result, list):
                for res in result:
                    msg = u"""查询单据结果-结果代码:%s,结果说明: %s""" % (res['resultCode'], res['resultMsg'])
                    # 判断指令状态
                    try:
                        if res['cmdStatus'] == '12':
                            msg = u"""单据%s,付款状态为（正在处理中),返回消息为:%s""" % (res['requestId'], res['resultMsg'])
                            self.alter_payment_state(form_code=res['requestId'], state=res['cmdStatus'], msg=msg)
                        elif res['cmdStatus'] == '14':
                            msg = u"""单据%s,付款状态为（处理成功）,返回消息为:%s""" % (res['requestId'], res['resultMsg'])
                            self.alter_payment_state(form_code=res['requestId'], state=res['cmdStatus'], msg=msg)
                        elif res['cmdStatus'] == '15':
                            msg = u"""单据%s,付款状态为（处理失败),返回消息为:%s""" % (res['requestId'], res['resultMsg'])
                            self.alter_payment_state(form_code=res['requestId'], state=res['cmdStatus'], msg=msg)
                        else:
                            msg = u"""自动任务: 单据%s,付款状态为（指令不存在 或 已收到未处理),返回消息为:%s""" % (
                                res['requestId'], res['resultMsg'])
                            self.alter_payment_state(form_code=res['requestId'], state=res['cmdStatus'], msg=msg)
                        logging.info(msg)
                        self.create_interface_bank_payment_log(res['requestId'], msg)
                    except KeyError:
                        logging.info(msg)
                        self.create_interface_bank_payment_log(res['requestId'], msg)
        logging.info(u"结束定时拉取银行付款状态任务...")
        return True

    @api.model
    def create_interface_bank_payment_log(self, form_code, msg):
        """创建付款确认时的日志记录
        :param form_code: 单据编码
        :param msg: 消息
        """
        payment = self.env['interface.bank.payment'].sudo().search([('form_code', '=', form_code)])
        data = {
            'form_code': form_code,
            'transaction_type': '01',  # 类型：00-付款，01-查询
            'stated': msg,
        }
        if payment:
            data['company_id'] = payment.company_id.id
        self.env['interface.bank.log'].sudo().create(data)
        return True

    @api.multi
    def alter_payment_state(self, form_code, state, msg):
        if state == '14':
            # 处理成功
            payment = self.env['interface.bank.payment'].sudo().search([('form_code', '=', form_code)])
            payment[0].sudo().write({'state': '02'})
            payment[0].sudo().message_post(body=msg, message_type='notification')
        elif state == '15':
            # 处理失败
            payment = self.env['interface.bank.payment'].sudo().search([('form_code', '=', form_code)])
            payment[0].sudo().write({'state': '03'})
            payment[0].sudo().message_post(body=msg, message_type='notification')
        elif state == '16':
            payment = self.env['interface.bank.payment'].sudo().search([('form_code', '=', form_code)])
            payment[0].sudo().write({'state': '03'})
            payment[0].sudo().message_post(body=msg, message_type='notification')
        elif state == '12':
            payment = self.env['interface.bank.payment'].sudo().search([('form_code', '=', form_code)])
        else:
            payment = self.env['interface.bank.payment'].sudo().search([('form_code', '=', form_code)])
            payment[0].sudo().message_post(body=msg, message_type='notification')
        return True

    @api.multi
    def serach_payment_result(self, number_array):
        """封装查询付款单状态的xml"""
        csystem_code = self.env['ir.values'].sudo().get_default('interface.bank.settings', 'csystem_code')
        csystem_name = self.env['ir.values'].sudo().get_default('interface.bank.settings', 'csystem_name')
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
