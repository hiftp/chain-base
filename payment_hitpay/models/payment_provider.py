# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import json
import hmac
import hashlib


import requests
from werkzeug import urls

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class Paymentprovider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('hitpay', "HitPay Payment Gateway")], ondelete={'hitpay': 'set default'}
    )

    hitpay_api_key = fields.Char(
        string="API Key", 
        required_if_provider='hitpay')
    
    hitpay_api_salt = fields.Char(
        string="Salt",
        required_if_provider='hitpay',
        groups='base.group_system')

    def _getApiURL(self):
        ctx_key = self.state
        ctx_value = 'https://api.sandbox.hit-pay.com/v1' if ctx_key == 'test' else 'https://api.hit-pay.com/v1'

        return ctx_value

    def _compute_feature_support_fields(self):
        """ Override of `payment` to enable additional features. """
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == 'hitpay').update({
            'support_refund': 'partial',
        })    
    
    def _hitpay_make_request(self, endpoint, payload=None, method='POST'):
        """ Make a request to HitPay API at the specified endpoint.

        Note: self.ensure_one()

        :param str endpoint: The endpoint to be reached by the request.
        :param dict payload: The payload of the request.
        :param str method: The HTTP method of the request.
        :return The JSON-formatted content of the response.
        :rtype: dict
        :raise ValidationError: If an HTTP error occurs.
        """
        self.ensure_one()

        url = self._getApiURL()+endpoint

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'X-BUSINESS-API-KEY': self.hitpay_api_key,
        }
        try:
            if method == 'GET':
                response = requests.get(url, params=payload, headers=headers, timeout=10)
            else:
                response = requests.post(url, data=dict(payload), headers=headers, timeout=10)
                _logger.info(
                    "Response for %s :\n%s",
                    endpoint, pprint.pformat(payload),
                )
                try:
                    response.raise_for_status()
                            
                except requests.exceptions.HTTPError:
                    _logger.exception(
                        "Invalid API request at %s with data:\n%s", url, pprint.pformat(payload),
                    )
                    response_content = response.json()
                    error_code = response_content.get('error')
                    error_message = response_content.get('message')
                    raise ValidationError("HitPay: " + _(
                        "The communication with the API failed. HitPay Payment Gateway gave us the following "
                        "information: '%s' (code %s)", error_message, error_code
                    ))
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            _logger.exception("Unable to reach endpoint at %s", url)
            raise ValidationError(
                "HitPay: " + _("Could not establish the connection to the API.")
            )
        

        return response.json()
    
    def _hitpay_calculate_signature(self, data):
        """ Compute the signature for the provided data according to the Hitpay documentation.

        :param dict data: The data to sign.
        :return: The calculated signature.
        :rtype: str
        """
        signing_string = ''
        for k in sorted(data.keys()):
            if k != 'hmac':
                signing_string += str(k)+''+str(data[k])

        signature = hmac.new(
            bytes(self.hitpay_api_salt, 'utf-8'),
            msg=bytes(signing_string, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        return signature
   