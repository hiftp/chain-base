# Part of Odoo. See LICENSE file for full copyright and licensing details.

import hmac
import logging
import pprint

from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request


_logger = logging.getLogger(__name__)


class HitpayController(http.Controller):
    _return_url = '/payment/hitpay/return'
    _webhook_url = '/payment/hitpay/webhook'

    @http.route(_return_url, type='http', methods=['GET'], auth='public')
    def hitpay_return_from_checkout(self, **data):
        """ Process the notification data sent by Hitpay after redirection from checkout.

        :param dict data: The notification data.
        """
        # Handle the notification data.
        _logger.info("Handling redirection from Hitpay with data:\n%s", pprint.pformat(data))
     
        if data.get('status') != 'canceled':
            return request.redirect('/payment/status')
        else:
            return request.redirect('/shop/payment')

    @http.route(
        f'{_webhook_url}/<reference>', type='http', auth='public', methods=['POST'], csrf=False
    )
    def hitpay_webhook(self, reference, **data):
        """ Process the notification data sent by Hitpay to the webhook.

        :param str reference: The transaction reference embedded in the webhook URL.
        :param dict _kwargs: The extra query parameters.
        :return: An empty string to acknowledge the notification.
        :rtype: str
        """
        _logger.info("Webhook received from Hitpay with data:\n%s", pprint.pformat(data))

        # Handle the notification data.
        try:
            # Check the integrity of the notification data.
            tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
                'hitpay', data
            )

            self._verify_notification_signature(data, tx_sudo)

            tx_sudo._handle_notification_data('hitpay', data)

        except ValidationError:  # Acknowledge the notification to avoid getting spammed.
            _logger.exception("Unable to handle the Hitpay  notification data; skipping to acknowledge")

        return 'Ok'  # Acknowledge the notification.
    
    @staticmethod
    def _verify_notification_signature(notification_data, tx_sudo):
        """ Check that the received signature matches the expected one.

        :param dict notification_data: The notification data
        :param recordset tx_sudo: The sudoed transaction referenced by the notification data, as a
                                  `payment.transaction` record
        :return: None
        :raise: :class:`werkzeug.exceptions.Forbidden` if the signatures don't match
        """
        received_signature = notification_data.get('hmac')
        if not received_signature:
            _logger.warning("Hitpay: Received notification with missing signature.")
            raise Forbidden()

        # Compare the received signature with the expected signature computed from the data.
        expected_signature = tx_sudo.provider_id._hitpay_calculate_signature(
            notification_data
        )
        if not hmac.compare_digest(received_signature, expected_signature):
            _logger.warning("Hitpay:Received notification with invalid signature.")
            raise Forbidden()
