# -*- coding: utf-8 -*-
import json

from pyexpat import ExpatError

from odoo import fields, models, api
from cqt_functions import CqtFunction as cqt
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PaymentCommit(models.TransientModel):
    _name = 'interface.payment.commit'
    _description = u"付款确认向导"

    FUNCTION_TYPE = [
        ('0', u'付款'),
        ('1', u'银行账户付款'),
        ('2', u'付款(代理)接口'),
    ]
    partner_id = fields.Char(string=u'收款户名:')
    partner_bank_number = fields.Char(string=u'收款账号:')
    pay_money = fields.Float(string=u'付款金额:')
    partner_contact = fields.Char(string=u'收款联系人')
    partner_contact_phone = fields.Char(string=u'联系人电话')
    partner_contact_add = fields.Char(string=u'联系人地址')

    bank_type = fields.Selection(string=u'付款银行', selection=[('00', u'财企通')], default='00')
    public_account_id = fields.Many2one(comodel_name='bank.public.accounts', string=u'付款账户', required=True)
    payment_type = fields.Selection(string=u'功能类型', selection=FUNCTION_TYPE, required=True, default='0')
    company_id = fields.Many2one(comodel_name='res.company', string=u'公司')

    @api.model
    def default_get(self, fields):
        """获取默认值"""
        res = super(PaymentCommit, self).default_get(fields)
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
            res.update({'company_id': payment.company_id.id})
            return res

    @api.onchange('bank_type', 'company_id')
    def onchange_bank_type(self):
        """当付款银行字段发生改变时，过滤付款账户。并赋默认值"""
        for res in self:
            res.public_account_id = False
            if res.bank_type:
                accs = self.env['bank.public.accounts'].sudo().search(
                    [('btype', '=', res.bank_type), ('company_id', '=', res.company_id.id)])
                if accs:
                    res.public_account_id = accs[0]
                domain = [('btype', '=', res.bank_type), ('company_id', '=', res.company_id.id)]
                return {'domain': {'public_account_id': domain}}

    @api.multi
    def summit_payment(self):
        """确认付款功能函数"""
        # 获取付款单对象
        payment = self.env['interface.bank.payment'].browse(self.env.context.get('active_id', False))
        msg = False
        # 判断选择银行
        if self.bank_type == '00':
            # 判断功能类型
            payment_type = self.payment_type
            # 获取财企通前置机地址
            service_url = self.env['ir.values'].get_default('interface.bank.settings', 'feg_add')
            if payment_type == '0':
                logging.info(u"付款类型为--付款--")
                efmp_xml = cqt.package_payment_to_xml(payment=payment, public_account=self.public_account_id)
                logging.info(efmp_xml)
                # 发送报文到前置机
                result_xml = cqt.send_xml_to_cqtbankservice(efmp_xml, service_url)
            elif payment_type == '1':
                logging.info(u"付款类型为--银行账户付款--")
                # 因银行账户付款接口需要传递收款方的详细信息，所以在生成xml前先检查付款单的数据是否齐全
                self.check_payment_fields(payment)
                efmp_xml = cqt.package_bank_account_payment_to_xml(payment, self.public_account_id)
                logging.info(efmp_xml)
                # 发送报文到前置机
                # 将xml字符串发送到财企通并接受结果xml
                result_xml = cqt.send_xml_to_cqtbankservice(efmp_xml, service_url)
            elif payment_type == '2':
                logging.info(u"付款类型为--付款代理接口--")
                efmp_xml = cqt.package_agent_payment_to_xml(payment, self.public_account_id)
                logging.info(efmp_xml)
                # 发送报文到前置机
                result_xml = cqt.send_xml_to_cqtbankservice(efmp_xml, service_url)
            # 解析xml
            try:
                result_data = self.parsing_general_instruction_messages(result_xml)
                self.check_execution_result(result_data, payment)
            except KeyError as e:
                raise UserError(u"交易发生KeyError异常！\r\n消息KeyError字段：{}".format(e.message))
            except ExpatError as e:
                raise UserError(u"财企通服务器通信故障！请检查前置机日志输出!\r\n{}".format(e.message))
        # 回写付款单状态
        payment_data = {
            'bank_type': self.bank_type,
            'public_account_id': self.public_account_id.id,
            'payment_type': self.payment_type,
        }
        payment.sudo().write(payment_data)
        self.create_interface_bank_payment_log(payment, msg)

    @api.model
    def check_payment_fields(self, payment):
        """检查付款单的数据是否正确
        :param payment: 付款单
        """
        if not payment.payee_bank:
            raise UserError(u"付款单中收款方归属银行不能为空!")
        if not payment.payee_opening_bank:
            raise UserError(u"付款单中收款方开户行字段不能为空!")
        if not payment.payee_opening_province:
            raise UserError(u"付款单中收款方省份字段不能为空!")
        if not payment.payee_opening_city:
            raise UserError(u"付款单中收款方城市字段不能为空!")

    @api.model
    def create_interface_bank_payment_log(self, payment, msg):
        """创建付款确认时的日志记录
        :param payment: 付款单
        :param msg: 消息
        """
        data = {
            'company_id': payment.company_id.id,
            'bank_type': payment.bank_type,
            'public_account_id': payment.public_account_id.id,
            'form_code': payment.form_code,
            'transaction_type': '00',  # 类型：00-付款，01-查询
            'partner_id': payment.partner_id,
            'partner_bank_number': payment.partner_bank_number,
            'pay_money': payment.pay_money,
            'stated': msg,
        }
        self.env['interface.bank.log'].sudo().create(data)
        return True

    @api.multi
    def parsing_general_instruction_messages(self, result_xml):
        """解析异步指令通用响应报文
        :param result_xml: 结果xml
        :return dict: 返回结果字典
        """
        result_json = cqt.xml_to_json(result_xml)
        result_json = json.loads(result_json.strip())
        efmp = result_json['efmp']
        body = efmp['body']
        result_set = body['resultSet']
        result = result_set['result']
        if isinstance(result, dict):
            return result

    @api.multi
    def check_execution_result(self, result_data, payment):
        if result_data['resultCode'] == '0000':
            if result_data.has_key('cmdStatus'):
                # 交易状态14代表支付成功
                if result_data.get('cmdStatus') == '14':
                    self.write({'state': '02'})
                    self.sudo().message_post(body=result_data.get('resultMsg'), message_type='notification')
                elif result_data.get('cmdStatus') == '11':
                    payment.sudo().write({'state': '01'})
                    msg = u"银行已收到信息但暂时未处理，返回信息:'{}'".format(result_data.get('resultMsg'))
                    payment.message_post(body=msg, message_type='notification')
                elif result_data.get('cmdStatus') == '12':
                    payment.sudo().write({'state': '01'})
                    msg = u"银行已收到信息正在处理中，返回信息:'{}'".format(result_data.get('resultMsg'))
                    payment.message_post(body=msg, message_type='notification')
                elif result_data.get('cmdStatus') == '15':
                    raise UserError(u"银行处理信息失败，返回信息:'{}'".format(result_data.get('resultMsg')))
                elif result_data.get('cmdStatus') == '16':
                    raise UserError(u"指令不存在，返回信息:'{}'".format(result_data.get('resultMsg')))
                else:
                    raise UserError(u"银行处理信息失败，返回信息:'{}'".format(result_data.get('resultMsg')))
            else:
                raise UserError(u"交易异常！请稍后查询手动支付结果，返回信息:'{}'".format(result_data.get('resultMsg')))
        else:
            msg = u"""执行失败！反馈代码: (%s),反馈消息: (%s)""" % (result_data['resultCode'], result_data['resultMsg'])
            logging.info(msg)
            raise UserError(msg)
        # if result_data['resultCode'] == '0000':
        #     msg = u"""执行成功！反馈代码: (%s),反馈消息: (%s)""" % (result_data['resultCode'], result_data['resultMsg'])
        #     logging.info(msg)
        #     payment.sudo().write({'state': '01'})
        #     payment.message_post(body=msg, message_type='notification')
        # else:
        #     msg = u"""执行失败！反馈代码: (%s),反馈消息: (%s)""" % (result_data['resultCode'], result_data['resultMsg'])
        #     logging.info(msg)
        #     raise UserError(msg)


class XPaymentCommit(models.TransientModel):
    _name = 'interface.xianxia.payment.commit'
    _description = u"线下付款确认"

    partner_id = fields.Char(string=u'收款户名:')
    partner_bank_number = fields.Char(string=u'收款账号:')
    pay_money = fields.Float(string=u'付款金额:')
    partner_contact = fields.Char(string=u'收款联系人')
    partner_contact_phone = fields.Char(string=u'联系人电话')
    partner_contact_add = fields.Char(string=u'联系人地址')

    move_name = fields.Char(string=u'付款科目')
    is_read = fields.Boolean(string=u'已使用付款科目')
    payment_type = fields.Char(string=u'付款方式', required=True)
    # 修改显示名称
    # author:fengjiqiang@inspur.com
    payment_money = fields.Float(string=u'本次付款金额', required=True)
    # end
    # payment_money = fields.Float(string=u'付款金额', required=True)
    payment_stated = fields.Text(string=u'备注消息')

    @api.model
    def default_get(self, fields):
        """获取默认值"""
        res = super(XPaymentCommit, self).default_get(fields)
        payment_id = self.env.context.get('active_id', False)
        payment = self.env['interface.bank.payment'].browse(payment_id)
        # 获取付款凭证科目
        if payment.move_id:
            # 获取凭证的贷方科目
            for move_line in payment.move_id.line_ids:
                if move_line.credit != 0:
                    res.update({'move_name': move_line.account_id.name})
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
            # 修改付款金额取数
            # author:fengjiqiang@inspur.com
            res.update({'payment_money': payment.pay_per_money_sum})
            # end
            # res.update({'payment_money': payment.pay_money})
            return res

    @api.multi
    def summit_payment(self):
        """使用线下支付确认功能"""
        if self.is_read:
            payment = self.env['interface.bank.payment'].browse(self.env.context.get('active_id', False))
            # 回写付款单状态
            msg = u"""已使用线下支付的方式进行了付款,支付金额为%s,备注信息：%s""" % (self.payment_money, self.payment_stated)
            # payment_data = {
            #     'state': '02',
            #     'payment_type': '01',
            #     'payment_stated': msg,
            # }
            # 回写状态以及判断条件
            # author:fengjiqiang@inspur.com
            if not self.payment_money:
                raise UserError("本次付款金额不能为0！")
            for line in payment.payment_line_ids:
                if line.state == 'done':
                    line.write({'state': 'paied'})
            # 计算字段已支付金额
            payment_money = payment.paied_money + payment.pay_per_money_sum
            # payment.write({'paied_money': payment_money, 'pay_per_money_sum': 0})
            payment.write({'paied_money': payment_money})
            # 增加判断 如果多次付款，状态更新为04分期付款(新增状态)，否则更新为02交易成功
            if payment.pay_remain_money > 0:
                payment_data = {
                    'state': '04',
                    'payment_type': '01',
                    'payment_stated': msg,
                }
            else:
                payment_data = {
                    'state': '02',
                    'payment_type': '01',
                    'payment_stated': msg,
                }
            # end
            payment.sudo().write(payment_data)
            payment.message_post(body=msg, message_type='notification')
            # 付款状态回写更新
            # author:fengjiqiang@inspur.com
            payment.update_payment()
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'interface.bank.payment',
                'view_mode': 'form',
                'target': 'current',
                'res_id': payment.id,
            }
            # end
        else:
            raise UserError(u"请确认已使用付款科目进行付款！")
