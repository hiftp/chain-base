# -*- coding: utf-8 -*-
import logging
import pprint
import requests
import qrcode
from io import BytesIO
import base64
import json

from odoo import _, http
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class IoTPayController(http.Controller):
    _return_url = '/payment/iotpay/return'
    _notify_url = '/payment/iotpay/notify'

    @http.route(_return_url, type='http', auth="public", methods=['GET'])
    def iotpay_return_from_redirect(self, **data):
        """ IoTPay return """
        _logger.info("received IoTPay return data:\n%s", pprint.pformat(data))
        #request.env['payment.transaction'].sudo()._handle_feedback_data('iotpay', data)
        return request.redirect('/payment/status')

    @http.route(_notify_url, type='http', auth='public', methods=['POST'], csrf=False)
    def iotpay_notify(self, **post):
        """ IoTPay Notify """
        _logger.info("received IoTPay notification data:\n%s", pprint.pformat(post))
        request.env['payment.transaction'].sudo()._handle_feedback_data('iotpay', post)
        return 'success'  # Return 'success' to stop receiving notifications for this tx

    @http.route('/payment/iotpay/qrcode', type='http', auth="public", website=True, methods=['GET'])
    def iotpay_qrcode_pay(self, order, qrurl, amount):
        """ User scan qrcode to pay """
        def make_qrcode(url):
            img = qrcode.make(url)
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            heximage = base64.b64encode(buffer.getvalue())
            return "data:image/png;base64,{}".format(heximage.decode('utf-8'))

        values = {}
        values['qrcode'] = make_qrcode(qrurl)
        values['order'] = order
        values['amount'] = amount
        return request.render("payment_iotpay.iotpay_qrcode", values)

    @http.route('/payment/iotpay/result', type='http', auth="public", website=True)
    def iotpay_query(self, order):
        """query payment result from page"""
        tx = request.env['payment.transaction'].sudo().search([('reference', '=', order), ('provider', '=', 'iotpay')])
        if tx and tx.state == 'done':
            # 支付成功
            return json.dumps({"result": 0, "order": order})
        return json.dumps({"result": 1, "order": order})
