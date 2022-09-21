# -*- coding: utf-8 -*-
import json

import requests
from odoo import fields, models, api
import logging
import datetime
from cqt_functions import CqtFunction as cqt
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class InterfaceBankPayment(models.Model):
    _name = 'interface.bank.payment'
    _inherit = 'mail.thread'
    _rec_name = 'form_code'
    _description = u'银行付款单'

    @api.multi
    def _get_default_currency(self):
        currency = self.env['bank.currency'].search([('code', '=', 'CNY')])
        return currency[0].id

    PAYMENTSTATE = [
        ('approval', u'待审核'),
        ('00', u'待付款'),
        ('04', u'分期付款'),
        ('01', u'银行确认'),
        ('02', u'交易成功'),
        ('03', u'交易失败')
    ]
    FUNCTION_TYPE = [
        ('0', u'付款'),
        ('1', u'银行账户付款'),
        ('2', u'付款(代理)接口'),
        ('01', u'线下支付'),
        ('a1', u'集团内汇兑-单笔'),
        ('a2', u'汇兑-单笔对公'),
        ('a3', u'汇兑-单笔对私'),
    ]
    public_signs = fields.Selection(string=u'公私标识', selection=[('00', u'对公'), ('01', u'对私'), ], default='00')
    payment_model = fields.Selection(string=u'付款模式', selection=[('01', u'普通'), ('02', u'加快'), ], default='01')
    cross_row_identi = fields.Selection(string=u'跨行标识', selection=[('0', u'本行'), ('1', u'跨行'), ], default='0')
    off_site_identi = fields.Selection(string=u'异地标识', selection=[('0', u'异地'), ('1', u'同城'), ], default='0')
    payee_identi = fields.Selection(string=u'收款方标识', selection=[('01', u'对外付款'), ('02', u'对内转账'), ], default='01')
    debit_identi = fields.Selection(string=u'借贷标识', selection=[('D', u'借'), ('C', u'贷'), ], default='D')
    payee_bank = fields.Char(string=u'收款方归属银行名称')
    payee_bank_code = fields.Char(string=u'收款方归属银行代码')
    payee_opening_bank = fields.Char(string=u'收款方开户行名称')
    payee_opening_bank_code = fields.Char(string=u'收款方开户行代码')
    payee_opening_province = fields.Char(string=u'收款方省份名称')
    payee_opening_province_code = fields.Char(string=u'收款方省份代码(财企通)')
    abc_provincial_code = fields.Char(string=u'收款方省份代码(农行)')
    payee_opening_city = fields.Char(string=u'收款方城市名称')
    payee_opening_city_code = fields.Char(string=u'收款方城市代码(财企通)')
    abc_city_code = fields.Char(string=u'收款方城市代码(农行)')
    currency_type = fields.Many2one(string=u'交易币种', comodel_name='bank.currency', required=True,
                                    default=_get_default_currency)
    company_id = fields.Many2one(comodel_name='res.company', string=u'公司',
                                 default=lambda self: self.env.user.company_id.id)
    partner_id = fields.Char(string=u'收款户名', required=True)
    partner_bank_number = fields.Char(string=u'收款账号', required=True)
    partner_number = fields.Char(string=u'客户编号', required=True)
    partner_contact = fields.Char(string=u'收款联系人')
    partner_contact_phone = fields.Char(string=u'联系人电话')
    partner_contact_add = fields.Char(string=u'联系人地址')
    pay_money = fields.Float(string=u'付款金额', digits=(23, 2))
    pay_summary = fields.Text(string=u'摘要')
    pay_use = fields.Char(string=u'付款用途')
    external_system_from = fields.Selection(string=u'外部系统传入', selection=[('y', u'是'), ('n', u'否'), ], default='n')
    form_code = fields.Char(string=u'单据编号')
    source_number = fields.Char(string=u'来源单据编号')
    source_model = fields.Char(string=u'来源单据模型')
    state = fields.Selection(string=u'单据状态', selection=PAYMENTSTATE, default='approval')
    bank_type = fields.Selection(string=u'付款银行', selection=[('00', u'财企通'), ('01', u'农业银行'), ('02', u'线下支付')],
                                 compute='_compute_bank_type', default='02')
    public_account_id = fields.Many2one(comodel_name='bank.public.accounts', string=u'付款账户')
    payment_type = fields.Selection(string=u'功能类型', selection=FUNCTION_TYPE)
    payment_stated = fields.Text(string=u'付款备注')
    save_datetime = fields.Date(string=u'生成日期', default=datetime.datetime.now())
    move_id = fields.Many2one(comodel_name='account.move', string=u'付款凭证', compute='_compute_account_move')
    # 增加支付记录
    # author: fengjiqiang@inspur.com
    payment_line_ids = fields.One2many('interface.bank.payment.line', 'payment_id', string=u"支付记录")
    paied_money = fields.Float(string=u"已付款金额", default=0, store=True)
    pay_remain_money = fields.Float(string=u"待付款金额", compute='_compute_remain_money', store=True)
    pay_per_money_sum = fields.Float(string=u"本次待支付金额", default=0, compute='_compute_paied_money', store=True)

    @api.depends('payment_line_ids')
    def _compute_paied_money(self):
        self.pay_per_money_sum = 0
        for line in self.payment_line_ids:
            if line.state == 'done':
                self.pay_per_money_sum += line.pay_per_money

    @api.depends('paied_money')
    def _compute_remain_money(self):
        self.pay_remain_money = self.pay_money - self.paied_money

    @api.multi
    def update_payment(self):
        """反写OA付款单"""
        update_payment_state_url = self.env['ir.values'].get_default('interface.bank.settings', 'update_payment_state')
        if not update_payment_state_url:
            raise UserError(u"请先配置银企直连付款状态反写OA付款单!")
        for res in self:
            payment_line_sets = []
            # 如果银企直连的支付记录状态为unpaied，则反写OA付款记录为submitted
            # 否则，状态一致
            for line in res.payment_line_ids:
                if line.state == 'unpaied':
                    payment_line_sets.append("submitted")
                else:
                    payment_line_sets.append(line.state)
            # 封装请求数据
            # state为支付记录状态
            pay_data = {
                "source_number": res.source_number if res.source_number else '',
                "paied_money": res.paied_money,
                "state": payment_line_sets
            }
            # 如果全部支付完，则在pay_data中新增一个字段payment_state
            # 并设置为02支付成功
            if res.state == '02':
                pay_data['payment_state'] = '02'
            try:
                logging.info(pay_data)
                headers = {'Content-Type': 'application/json'}
                result = requests.post(url=update_payment_state_url, headers=headers, data=json.dumps(pay_data))
            except TypeError as e:
                raise UserError(u"TypeError异常错误,可能原因是付款状态更新地址不正确！返回信息：{}".format(e.message))
            except Exception as e:
                raise UserError(u'付款状态更新失败: 失败原因：'.format(e.message))
            try:
                result = json.loads(result.text)
                result = json.loads(result.get('result'))
                logging.info("result:{}".format(result))
                res.message_post(body=result['message'], message_type='notification')
                if result.get('code') != '0000':
                    raise UserError(u"付款状态反写失败,错误详情：{}".format(result.get('message')))
            except KeyError as e:
                raise UserError(u"KeyError异常错误：{}".format(e.message))
            except TypeError as e:
                raise UserError(u"TypeError OA系统返回了错误信息！返回信息：{}".format(e.message))
        # 更新pay_per_money_sum字段值
        self._compute_paied_money()
    # end

    @api.multi
    def pay_again(self):
        group = self.env.user.has_group('interface_bank.approval_payment_group')
        if group:
            for res in self:
                res.write({'state': '03'})
                # 审核不通过后，变更明细中的状态为undone未过审
                # @author: fengjiqiang@inspur.com
                for line in res.payment_line_ids:
                    if line.state == 'unpaied':
                        line.write({'state': 'undone'})
                # end
                msg = u"提示：{}于{}拒绝审核了单据.".format(self.env.user.name,
                                                 datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                res.message_post(body=msg, message_type='notification')
            # 审核不通过后，同时回写记录中付款状态
            # @author: fengjiqiang@inspur.com
            self.update_payment()
            # end
        else:
            raise UserError(u"您不具备审核权限！需要《审核付款单》权限! \r\n 如果您认为这是一个错误，请联系管理员！")

    @api.model
    def create(self, vals):
        if vals['pay_money'] <= 0:
            raise UserError(u"付款金额不能小于等于0！")
        if not vals.get('form_code'):
            vals['form_code'] = self.env['ir.sequence'].sudo().next_by_code('interface.bank.payment')
        if not vals['partner_number']:
            vals['partner_number'] = self.env['ir.sequence'].sudo().next_by_code('interface.payment.partner.number')
        vals = self.relace_fislds(vals)
        return super(InterfaceBankPayment, self).create(vals)


    @api.model
    def relace_fislds(self, val):
        """
        去除字段的空格
        :param val:
        :return: val
        """
        val['payee_bank'] = val['payee_bank'].replace(' ', '')
        val['payee_bank_code'] = val['payee_bank_code'].replace(' ', '')
        val['payee_opening_bank'] = val['payee_opening_bank'].replace(' ', '')
        val['payee_opening_bank_code'] = val['payee_opening_bank_code'].replace(' ', '')
        val['payee_opening_province'] = val['payee_opening_province'].replace(' ', '')
        val['payee_opening_province_code'] = val['payee_opening_province_code'].replace(' ', '')
        val['abc_provincial_code'] = val['abc_provincial_code'].replace(' ', '')
        val['payee_opening_city'] = val['payee_opening_city'].replace(' ', '')
        val['payee_opening_city_code'] = val['payee_opening_city_code'].replace(' ', '')
        val['abc_city_code'] = val['abc_city_code'].replace(' ', '')
        val['partner_id'] = val['partner_id'].replace(' ', '')
        val['partner_bank_number'] = val['partner_bank_number'].replace(' ', '')
        return val

    @api.model
    def get_today_pay_money(self):
        """返回当天发生的付款金额"""
        now_time = datetime.datetime.now()
        payment = self.env['interface.bank.payment'].search([('save_datetime', '=', now_time.strftime('%Y-%m-%d'))])
        today_money = 0
        for pay in payment:
            today_money += pay.pay_money
        return {'today_money': today_money, 'payment_len': len(payment)}

    @api.model
    def get_new_payment(self):
        """获取最新的付款单"""
        sql = """
            SELECT
                payment.id, payment.form_code, payment.partner_id, payment.partner_bank_number, payment.pay_money  
            FROM
                interface_bank_payment payment
            WHERE
                state = '00'
            ORDER BY
                payment.create_date desc 
        """
        cr = self.env.cr
        cr.execute(sql)
        rel_results = cr.fetchall()
        number = 1
        data_list = list()
        for rel in rel_results:
            if number <= 10:
                data_list.append({
                    'form_number': rel[1],
                    'partner_id': rel[2],
                    'partner_bank_number': rel[3],
                    'pay_money': rel[4],
                })
                number += 1
            else:
                break
        return data_list

    @api.model
    def get_payment_result(self):
        """从日志中获取银行付款结果"""
        sql = """select  form_code,stated from interface_bank_log where transaction_type='01' and company_id = %s
        ORDER BY create_date DESC
        """ % (self.env.user.company_id.id)
        cr = self.env.cr
        cr.execute(sql)
        rel_results = cr.fetchall()
        data_list = list()
        i = 1
        for res in rel_results:
            if i > 10:
                break
            result_str = u"""%s, 状态： %s""" % (res[0], res[1])
            data_list.append({'result_str': result_str})
            i += 1
        return data_list

    @api.multi
    def update_from_code(self):
        """重新生成新的编号、单据流水号"""
        form_code = self.env['ir.sequence'].sudo().next_by_code('interface.bank.payment')
        self.write({'form_code': form_code})

    @api.depends('source_number', 'source_model')
    def _compute_account_move(self):
        for res in self:
            if res.source_number and res.source_model:
                sql = """select move_id 
                from account_preset_vousher_entry  where form_number='{}' and form_model = '{}' and amortization = '00'
                """.format(res.source_number, res.source_model)
                cr = self.env.cr
                cr.execute(sql)
                rel_results = cr.fetchall()
                for rel in rel_results:
                    res.move_id = rel[0]
                    return True

    @api.depends('move_id')
    def _compute_bank_type(self):
        """根据付款凭证的贷方科目获取出应使用的付款银行"""
        for res in self:
            if res.move_id:
                # 获取凭证的贷方科目
                for move_line in res.move_id.line_ids:
                    if move_line.credit != 0:
                        # 根据贷方科目到付款科目中查询付款银行
                        if move_line.account_id.user_type_id.name == u'银行和现金':
                            payment_account = self.env['interface.payment.account'].sudo().search(
                                [('account_code', '=', move_line.account_id.code)])
                            res.bank_type = payment_account[0].bank_type if payment_account else '02'
                            res.write({'pay_money': move_line.credit})
            else:
                res.bank_type = '02'

    @api.multi
    def approval_payment(self):
        group = self.env.user.has_group('interface_bank.approval_payment_group')
        if group:
            for res in self:
                res.write({'state': '00'})
                # 审核通过后，变更明细中的状态为done已过审
                # @author: fengjiqiang@inspur.com
                for line in res.payment_line_ids:
                    if line.state == 'unpaied':
                        line.write({'state': 'done'})
                # end
                msg = u"提示：{}于{}已审核了单据.".format(self.env.user.name,
                                                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                self.sudo().message_post(body=msg, message_type='notification')
            # 审核通过后，同时回写记录中付款状态
            # fengjiqiang@inspur.com
            self.update_payment()
            # end
        else:
            raise UserError(u"您不具备审核权限！需要《审核付款单》权限! \r\n 如果您认为这是一个错误，请联系管理员！")

    @api.multi
    def search_cqt_payment_result(self):
        """查询付款单据（财企通）支付结果"""
        # 将付款单据编号封装成xml
        xml_str = cqt.package_query_payment_result_to_xml([self.form_code])
        # 获取财企通前置机地址url
        service_url = self.env['ir.values'].get_default('interface.bank.settings', 'feg_add')
        if not service_url:
            raise UserError(u"请正确配置财企通前置机地址url")
        # 将xml字符串发送到财企通并接受结果xml
        result_xml = cqt.send_xml_to_cqtbankservice(xml_str, service_url)
        # 解析xml
        result_json = cqt.xml_to_json(result_xml)
        result_json = json.loads(result_json.strip())
        efmp = result_json['efmp']
        body = efmp['body']
        result_set = body['resultSet']
        # 封装结果返回到页面
        result = result_set['result']
        if isinstance(result, dict):
            if result.get('resultCode') != '0000':
                self.write({'state': '03'})
                self.sudo().message_post(body=result.get('resultMsg'), message_type='notification')
                return False
            # 交易状态14代表支付成功
            if result.get('cmdStatus') == '14':
                self.write({'state': '02'})
                self.sudo().message_post(body=result.get('resultMsg'), message_type='notification')
            elif result.get('cmdStatus') == '11':
                raise UserError(u"银行已收到信息但暂时未处理，返回信息:'{}'".format(result.get('resultMsg')))
            elif result.get('cmdStatus') == '12':
                raise UserError(u"银行已收到信息正在处理中，返回信息:'{}'".format(result.get('resultMsg')))
            elif result.get('cmdStatus') == '15':
                self.write({'state': '03'})
                self.sudo().message_post(body=result.get('resultMsg'), message_type='notification')
                # raise UserError(u"银行处理信息失败，返回信息:'{}'".format(result.get('resultMsg')))
            elif result.get('cmdStatus') == '16':
                raise UserError(u"查询指令不存在，返回信息:'{}'".format(result.get('resultMsg')))

    @api.multi
    def unlink(self):
        raise UserError(u"系统不允许删除付款单!")
