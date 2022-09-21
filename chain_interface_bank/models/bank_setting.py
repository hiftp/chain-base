# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class BankSettings(models.TransientModel):
    _name = 'interface.bank.settings'
    _inherit = 'res.config.settings'

    feg_add = fields.Char(string=u'财企通前置机地址')
    csystem_code = fields.Char(string=u'查询类系统代码(财企通)')
    csystem_name = fields.Char(string=u'查询类系统名称(财企通)')
    p_csystem_code = fields.Char(string=u'付款和查询系统代码(财企通)')
    p_csystem_name = fields.Char(string=u'付款和查询系统名称(财企通)')
    auto_read_payment = fields.Selection(string=u'自动读取银行付款状态', selection=[('y', u'开启'), ('n', u'不开启')])
    interval_number = fields.Integer(string=u'间隔数')
    interval_type = fields.Selection([('minutes', u'分钟'), ('hours', u'小时'), ('work_days', u'工作日'), ('days', u'天数'),
                                      ('weeks', u'周'), ('months', u'月')], string=u'间隔单位', default='days')

    open_interface = fields.Selection(string=u'是否允许外部系统传入付款单', selection=[('y', u'允许'), ('n', u'不允许')])
    search_payment = fields.Selection(string=u'是否允许外部查询付款单状态', selection=[('y', u'允许'), ('n', u'不允许')])
    open_callback = fields.Selection(string=u'是否允许回调付款状态(外部系统)', selection=[('y', u'允许'), ('n', u'不允许')])

    abc_ip = fields.Char(string=u'农行企业通讯器ICT地址')
    abc_port = fields.Char(string=u'农行企业通讯器端口')
    abc_operator_number = fields.Char(string=u'企业操作员编号')
    abc_auth_no = fields.Char(string=u'认证码')
    abc_sign = fields.Char(string=u'数字签名')
    ftp_host = fields.Char(string=u'前置机FTP地址')
    ftp_port = fields.Integer(string=u'前置机FTP端口')
    ftp_user = fields.Char(string=u'前置机FTP用户名')
    ftp_pwd = fields.Char(string=u'前置机FTP用户密码')
    dir_ftp = fields.Char(string=u'前置机FTP文件下载目录')
    dir_up_ftp = fields.Char(string=u'前置机FTP文件上传目录')
    # 增加字段：更新付款状态至OA地址
    # @author: fengjiqiang@inspur.com
    update_payment_state = fields.Char(string=u'更新付款状态至OA地址')
    # end

    @api.multi
    def get_default_params(self, fields):
        ir_values = self.env['ir.values']
        return {
            'feg_add': ir_values.get_default('interface.bank.settings', 'feg_add') or str(
                'http://127.0.0.1:8088/efmp-feg-front-war/fegSrvServlet'),
            'csystem_code': ir_values.get_default('interface.bank.settings', 'csystem_code') or 'test',
            'csystem_name': ir_values.get_default('interface.bank.settings', 'csystem_name') or 'test',
            'auto_read_payment': ir_values.get_default('interface.bank.settings', 'auto_read_payment') or 'y',
            'interval_number': ir_values.get_default('interface.bank.settings', 'interval_number') or 30,
            'interval_type': ir_values.get_default('interface.bank.settings', 'interval_type') or 'minutes',
            'open_interface': ir_values.get_default('interface.bank.settings', 'open_interface') or 'y',
            'search_payment': ir_values.get_default('interface.bank.settings', 'search_payment') or 'y',
            'open_callback': ir_values.get_default('interface.bank.settings', 'open_callback') or 'n',
            'abc_ip': ir_values.get_default('interface.bank.settings', 'abc_ip') or '10.193.10.211',
            'abc_port': ir_values.get_default('interface.bank.settings', 'abc_port') or '15999',
            'p_csystem_code': ir_values.get_default('interface.bank.settings', 'p_csystem_code') or '',
            'p_csystem_name': ir_values.get_default('interface.bank.settings', 'p_csystem_name') or '',
            'abc_operator_number': ir_values.get_default('interface.bank.settings', 'abc_operator_number') or '',
            'abc_auth_no': ir_values.get_default('interface.bank.settings', 'abc_auth_no') or '',
            'abc_sign': ir_values.get_default('interface.bank.settings', 'abc_sign') or '',
            'ftp_host': ir_values.get_default('interface.bank.settings', 'ftp_host') or '1.1.1.1',
            'ftp_port': ir_values.get_default('interface.bank.settings', 'ftp_port') or 21,
            'ftp_user': ir_values.get_default('interface.bank.settings', 'ftp_user') or '',
            'ftp_pwd': ir_values.get_default('interface.bank.settings', 'ftp_pwd') or '',
            'dir_ftp': ir_values.get_default('interface.bank.settings', 'dir_ftp') or '/',
            'dir_up_ftp': ir_values.get_default('interface.bank.settings', 'dir_up_ftp') or '/',
            # 更新付款状态至OA地址，获取url默认值
            # @author: fengjiqiang@inspur.com
            'update_payment_state': ir_values.get_default('interface.bank.settings', 'update_payment_state') or
                                    'http://ip:port/oa/interface/payment/update/state',
            # end
        }

    @api.multi
    def execute(self):
        if self.auto_read_payment == 'y':
            # ------添加定时拉取银行付款状态自动任务----
            data = {
                'name': u'定时拉取银行付款状态自动任务(银企直联)',
                'active': True,
                'user_id': 1,
                'interval_number': self.interval_number,
                'interval_type': self.interval_type,
                'model': 'interface.bank.automate.tasks',
                'function': 'automate_update_payment_state',
                'numbercall': -1,
            }
            cron = self.env['ir.cron'].sudo().search(
                [('model', '=', 'interface.bank.automate.tasks'), ('function', '=', 'automate_update_payment_state')])
            if len(cron) < 1:
                self.env['ir.cron'].sudo().create(data)
            elif len(cron) >= 1:
                cron.sudo().write(data)
        else:
            cron = self.env['ir.cron'].sudo().search(
                [('model', '=', 'interface.bank.automate.tasks'), ('function', '=', 'automate_update_payment_state')])
            if len(cron) >= 1:
                cron.sudo().unlink()
        return super(BankSettings, self).execute()

    # 更新付款状态至OA地址，设置url默认值
    # @author: fengjiqiang@inspur.com
    @api.multi
    def set_update_payment_state(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'update_payment_state', self.update_payment_state)
    # end

    @api.multi
    def set_feg_add(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'feg_add', self.feg_add)

    @api.multi
    def set_p_csystem_code(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'p_csystem_code', self.p_csystem_code)

    @api.multi
    def set_p_csystem_name(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'p_csystem_name', self.p_csystem_name)

    @api.multi
    def set_csystem_code(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'csystem_code', self.csystem_code)

    @api.multi
    def set_csystem_name(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'csystem_name', self.csystem_name)

    @api.multi
    def set_auto_read_payment(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'auto_read_payment', self.auto_read_payment)

    @api.multi
    def set_interval_number(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'interval_number', self.interval_number)

    @api.multi
    def set_interval_type(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'interval_type', self.interval_type)

    @api.multi
    def set_open_interface(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'open_interface', self.open_interface)

    @api.multi
    def set_search_payment(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'search_payment', self.search_payment)

    @api.multi
    def set_open_callback(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'open_callback', self.open_callback)

    @api.multi
    def set_abc_ip(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'abc_ip', self.abc_ip)

    @api.multi
    def set_abc_port(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'abc_port', self.abc_port)

    @api.multi
    def set_abc_operator_number(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'abc_operator_number', self.abc_operator_number)

    @api.multi
    def set_abc_auth_no(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'abc_auth_no', self.abc_auth_no)

    @api.multi
    def set_abc_sign(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'abc_sign', self.abc_sign)

    @api.multi
    def set_ftp_host(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'ftp_host', self.ftp_host)

    @api.multi
    def set_ftp_port(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'ftp_port', self.ftp_port)

    @api.multi
    def set_ftp_user(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'ftp_user', self.ftp_user)

    @api.multi
    def set_ftp_pwd(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'ftp_pwd', self.ftp_pwd)

    @api.multi
    def set_dir_ftp(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'dir_ftp', self.dir_ftp)

    @api.multi
    def set_dir_up_ftp(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'interface.bank.settings', 'dir_up_ftp', self.dir_up_ftp)
