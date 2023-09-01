# -*- coding: utf-8 -*-
import logging
from hashlib import md5
from odoo import api, fields, models
from odoo.http import request

_logger = logging.getLogger(__name__)


class PaymentAcquirer(models.Model):
    _inherit = 'payment.provider'

    provider = fields.Selection(selection_add=[('iotpay', "IoTPay")], ondelete={'iotpay': 'set default'})
    iotpay_channel = fields.Selection(string="IOTPay Channel", required_if_provider='iotpay',
                                            selection=[('WX_JSAPI', "微信内网页支付"),
                                                            ('WX_MICROPAY', "商户扫描用户微信二维码"),
                                                            ('WX_NATIVE', "微信原生扫码支付(用户扫码)"),
                                                            ('WX_APP', "商户APP微信支付"),
                                                            ('ALIPAY_MOBILE', "商户APP支付宝支付"),
                                                            ('ALIPAY_PC', "支付宝PC支付"),
                                                            ('ALIPAY_WAP', "支付宝WAP支付"),
                                                            ('ALIPAY_QR', "支付宝原生扫码支付(用户扫码)"),
                                                            ('ALIPAY_MICROPAY', "商户扫描用户支付宝二维码"),
                                                            ('UPI_MICROPAY', "银联云闪付二维码(商户扫描用户)"),
                                                            ('UPI_QR', "银联云闪付二维码(用户扫商户)"),
                                                            ('UPI_SEQ', "银联卡在线安全支付(跳转到银联网页)"),
                                                            ('UPI_APP', "银联卡在线安全支付(使用银联SDK)"),
                                                            ('CC_PAX', "和信用卡刷卡终端集成"),
                                                            ] )
    iotpay_merchant_id = fields.Char(string="Merchant ID", required_if_provider='iotpay')
    iotpay_job_no = fields.Char(string="Merchant Job No")
    iotpay_md5_signature_key = fields.Char(
        string="MD5 Signature Key", required_if_provider='iotpay', groups='base.group_system')

    @api.model
    def _get_compatible_acquirers(self, *args, currency_id=None, **kwargs):
        """ Override of payment to unlist Alipay acquirers for unsupported currencies. 
             IOTPay 只支持 加元、美元和人民币
        """
        acquirers = super()._get_compatible_acquirers(*args, currency_id=currency_id, **kwargs)

        currency = self.env['res.currency'].browse(currency_id).exists()
        if currency and not currency.name in ['CNY', 'CAD', 'USD']:
            acquirers = acquirers.filtered(lambda a: a.provider != 'iotpay')

        agent = request.httprequest.environ['HTTP_USER_AGENT']
        if 'micromessenger' in  agent.lower():
            acquirers = acquirers.filtered(lambda a: a.provider == 'iotpay' and (a.iotpay_channel in ['WX_JSAPI', 'UPI_SEQ', 'ALIPAY_PC']))
        else:
            acquirers = acquirers.filtered(lambda a: a.provider == 'iotpay' and (a.iotpay_channel in ['WX_NATIVE', 'UPI_SEQ', 'ALIPAY_PC']))

        return acquirers

    def _iotpay_build_sign(self, val):
        # Rearrange parameters in the data set alphabetically
        data_to_sign = sorted(val.items())
        # Format key-value pairs of parameters that should be signed
        data_to_sign = [f"{k}={v}" for k, v in data_to_sign
                        if k not in ['sign', 'sign_type']]
        # Build the data string of &-separated key-value pairs
        data_string = '&'.join(data_to_sign)
        data_string += "&key=%s" % self.iotpay_md5_signature_key
        res = md5(data_string.encode('utf-8')).hexdigest()
        return res.upper()

    def _iotpay_get_api_url(self):
        if self.state == 'enabled':
            if self.iotpay_channel == 'WX_JSAPI':
                return 'https://api.iotpaycloud.com/v1/payForSubmit'
            else:
                return 'https://api.iotpaycloud.com/v1/create_order'
        else:  # test environment
            return ''

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'iotpay':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_iotpay.payment_method_iotpay').id
