# -*- coding: utf-8 -*-
import logging
from odoo.tools import float_compare
import json
import requests
from werkzeug import urls
from odoo.http import request
from odoo import _, api, models
from odoo.exceptions import ValidationError

from odoo.addons.payment_iotpay.controllers.main import IoTPayController

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_processing_values(self, processing_values):
        """ Override of payment to return Alipay-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific processing values
        :rtype: dict
        """
        super()._get_specific_processing_values(processing_values)
        if self.provider != 'iotpay':
            return res

        base_url = self.acquirer_id.get_base_url()
        base_url = base_url.replace('http', 'https')
        ip_addr = request.httprequest.environ['REMOTE_ADDR']
        rendering_values = {
            'mchId': self.acquirer_id.iotpay_merchant_id,  #商户ID
            'mchOrderNo': self.reference,   #商户订单号
            'currency': self.currency_id.name,   #币种
            'channelId': self.acquirer_id.iotpay_channel,   #支付渠道
            'amount': int(self.amount * 100),     #支付金额
            'clientIp': ip_addr,    #客户端IP
            'device': 'WEB',        #终端设备号(门店号或收银设备ID)，注意：PC网页或公众号内支付请传"WEB"
            'returnUrl': urls.url_join(base_url, IoTPayController._return_url),   #支付结束跳转URL
            'notifyUrl': urls.url_join(base_url, IoTPayController._notify_url),   #支付结果回调URL
            'subject': self.reference,   #商品主题
            'body': 'Delivery Fees',   #商品描述
            #'param1': '',   #扩展参数1，可忽略
            #'param2': '',   #扩展参数2，支付中心回调时会原样返回
            #'extra': '',       #微信小程序，WX_APP,WX_NATIVE需要
            #'jobNo': self.acquirer_id.iotpay_job_no,   #子账号
            #'remarks': '',     #商户的附言
            #'sign': ,  #签名
        }

        if self.acquirer_id.iotpay_job_no:
            rendering_values.update({'jobNo': self.acquirer_id.iotpay_job_no})

        sign = self.acquirer_id._iotpay_build_sign(rendering_values)
        url = self.acquirer_id._iotpay_get_api_url()
        rendering_values["sign"] = sign
        data_json = json.dumps(rendering_values)
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        params = "params=%s" % data_json
        res = requests.post(url=url, data=params, headers=headers)
        res_json = json.loads(res.text)
        #print(res_json)
        if res_json['retCode'] != 'SUCCESS':
            return res_json
        res_json['iotpay_url'] = res_json.get('url', '')
        if self.acquirer_id.iotpay_channel in ['ALIPAY_PC', 'ALIPAY_WAP']:
            res_json['iotpay_url'] = res_json['retParams']['alipayUrl']
        elif self.acquirer_id.iotpay_channel in ['UPI_SEQ',]:
            res_json['iotpay_url'] = res_json['retParams']['unionpayUrl']
        elif self.acquirer_id.iotpay_channel in  ['ALIPAY_QR', 'UPI_QR']:
            res_json['qrcode'] = res_json['qr_code']
        elif self.acquirer_id.iotpay_channel == 'WX_NATIVE':
            res_json['qrcode'] = res_json['codeUrl']
        if res_json.get('qrcode', False):   #生成支付二维码的URL
            params = {
                'order': self.reference,
                'qrurl': res_json['qrcode'],
                'amount': self.amount,
            }
            res_json['iotpay_url'] = '/payment/iotpay/qrcode?' + urls.url_encode(params)
        
        return res_json

    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        """ Override of payment to find the transaction based on Iotpay data.

        :param str provider: The provider of the acquirer that handled the transaction
        :param dict data: The feedback data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'iotpay':
            return tx

        payOrderId = data.get('payOrderId', False)
        mchOrderNo = data.get('mchOrderNo', False)
        channelOrderNo = data.get('channelOrderNo', False)
        
        if not payOrderId or not channelOrderNo:
            raise ValidationError(
                "IoTPay: " + _(
                    "Received data with missing payOrderId %(r)s or channelOrderNo %(t)s.",
                    r=payOrderId, t=channelOrderNo
                )
            )

        tx = self.search([('reference', '=', mchOrderNo), ('provider', '=', 'iotpay')])
        if not tx:
            raise ValidationError(
                "IoTPay: " + _("No transaction found matching reference %s.", mchOrderNo)
            )

        # Verify signature (done here because we need the reference to get the acquirer)
        sign_check = tx.acquirer_id._iotpay_build_sign(data)
        sign = data.get('sign')
        if sign != sign_check:
            raise ValidationError(
                "IoTPay: " + _(
                    "Expected signature %(sc) but received %(sign)s.", sc=sign_check, sign=sign
                )
            )

        return tx

    def _process_feedback_data(self, data):
        """ Override of payment to process the transaction based on Iotpay data.

        Note: self.ensure_one()

        :param dict data: The feedback data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._process_feedback_data(data)
        if self.provider != 'iotpay':
            return

        if float_compare(float(data.get('amount', '0.0')), self.amount * 100, 2) != 0:
            # mc_gross is amount + fees
            logging_values = {
                'amount': data.get('amount', '0.0'),
                'total': self.amount * 100,
                'fees': self.fees,
                'reference': self.reference,
            }
            _logger.error(
                "the paid amount (%(amount)s) does not match the total + fees (%(total)s + "
                "%(fees)s) for the transaction with reference %(reference)s", logging_values
            )
            raise ValidationError("IoTPay: " + _("The amount does not match the total + fees."))

        self.acquirer_reference = "%s : %s" % (data.get('channelOrderNo', False), data.get('payOrderId', False))
        status = data.get('status', False)
        if status == '2':
            self._set_done()
        else:
            _logger.info(
                "received invalid transaction status for transaction with reference %s: %s",
                self.reference, status
            )
            self._set_error("IoTPay: " + _("received invalid transaction status: %s", status))
