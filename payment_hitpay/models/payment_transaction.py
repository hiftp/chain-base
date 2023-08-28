# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint

from werkzeug import urls

from odoo import _, models, fields
from odoo.exceptions import ValidationError

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_hitpay.const import TRANSACTION_STATUS_MAPPING
from odoo.addons.payment_hitpay.controllers.main import HitpayController


_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    hitpay_payment_status = fields.Char(_('Hitpay Transaction Status'))
    hitpay_payment_id = fields.Char(_('Hitpay Payment ID'))
    hitpay_transaction_id = fields.Char(_('Hitpay Transaction ID'))
    hitpay_payment_request_id = fields.Char(_('Hitpay Payment Request ID'))
    hitpay_payment_amount = fields.Char(_('Hitpay Payment Amount'))
    hitpay_payment_currency = fields.Char(_('Hitpay Payment Currency'))
    hitpay_refund_id = fields.Char(_('Hitpay Refund ID'))
    hitpay_refund_amount = fields.Char(_('Hitpay Refunded Amount'))
    hitpay_refund_currency = fields.Char(_('Hitpay Refunded Currency'))
    hitpay_refund_createdat = fields.Char(_('Hitpay Refunded Date'))

    def _get_specific_rendering_values(self, processing_values):
        """ Override of `payment` to return Hitpay-specific rendering values.

        Note: self.ensure_one() from `_get_rendering_values`.

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific processing values.
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'hitpay':
            return res

        # Initiate the payment and retrieve the payment link data.
        payload = self._hitpay_prepare_preference_request_payload()

        
        payment_response = self.provider_id._hitpay_make_request(
            '/payment-requests', payload=payload
        )
        
        values = {
            'hitpay_payment_request_id': payment_response['id'],
        }
        self.write(values)

        # Extract the payment link URL and embed it in the redirect form.
        rendering_values = {
            'api_url': payment_response['url'],
        }
        return rendering_values

    def _hitpay_prepare_preference_request_payload(self):
        """ Create the payload for the preference request based on the transaction values.

        :return: The request payload.
        :rtype: dict
        """
        base_url = self.provider_id.get_base_url()
        return_url = urls.url_join(
            base_url, f'{HitpayController._return_url}'
        )
        webhook_url = urls.url_join(
            base_url, f'{HitpayController._webhook_url}/{self.reference}'
        )  # Append the reference to identify the transaction from the webhook notification data.

        return {
            'reference_number': self.reference,
            'amount': self.amount,
            'currency': self.currency_id.name,
            'redirect_url': return_url,
            'webhook': webhook_url,
            'name': self.partner_name,
            'email': self.partner_email,
            'channel': 'api_odoo'
        }

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of `payment` to find the transaction based on Hitpay data.

        :param str provider_code: The code of the provider that handled the transaction.
        :param dict notification_data: The notification data sent by the provider.
        :return: The transaction if found.
        :rtype: recordset of `payment.transaction`
        :raise ValidationError: If inconsistent data were received.
        :raise ValidationError: If the data match no transaction.
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'hitpay' or len(tx) == 1:
            return tx

        reference = notification_data.get('reference_number')
        if not reference:
            raise ValidationError("Hitpay: " + _("Received data with missing reference."))

        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'hitpay')])
        if not tx:
            raise ValidationError(
                "Hitpay: " + _("No transaction found matching reference %s.", reference)
            )
        return tx

    def _process_notification_data(self, notification_data):
        """ Override of `payment` to process the transaction based on Hitpay data.

        Note: self.ensure_one() from `_process_notification_data`

        :param dict notification_data: The notification data sent by the provider.
        :return: None
        :raise ValidationError: If inconsistent data were received.
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'hitpay':
            return

        payment_id = notification_data.get('payment_id')
        if not payment_id:
            raise ValidationError("Hitpay: " + _("Received data with missing payment id."))
        
        self.hitpay_payment_id = payment_id
        self.hitpay_transaction_id = payment_id
        self.hitpay_payment_status = notification_data.get('status')
        self.hitpay_payment_amount = notification_data.get('amount')
        self.hitpay_payment_currency = notification_data.get('currency')
        self.provider_reference = payment_id
        
        reference_number = notification_data.get('reference_number')
        
        payment_status = notification_data.get('status')

        if not payment_status:
            raise ValidationError("Hitpay: " + _("Received data with missing status."))

        message = "Payment successful. Transaction Id: "+self.hitpay_payment_id+", "
        message += "Amount Paid: "+self.hitpay_payment_amount

        if payment_status in TRANSACTION_STATUS_MAPPING['pending']:
            self._set_pending(state_message=message)
        elif payment_status in TRANSACTION_STATUS_MAPPING['done']:
            self._set_done(state_message=message)
        elif payment_status in TRANSACTION_STATUS_MAPPING['canceled']:
            self._set_canceled()
        else:  # Classify unsupported payment status as the `error` tx state.
            _logger.warning(
                "Hitpay: Received data for transaction with reference %s with invalid payment status: %s",
                reference_number, payment_status
            )
            self._set_error(
                "Hitpay: " + _("Received data with invalid status: %s", payment_status)
            )

    def _send_refund_request(self, amount_to_refund=None):
        """ Override of payment to send a refund request to Hitpay.

        Note: self.ensure_one()

        :param float amount_to_refund: The amount to refund
        :return: The refund transaction created to process the refund request.
        :rtype: recordset of `payment.transaction`
        """

        self.ensure_one()
        
        refund_tx = super()._send_refund_request(amount_to_refund=amount_to_refund)
        if self.provider_code != 'hitpay':
            return refund_tx

        # Make the refund request to Hitpay
        converted_amount = payment_utils.to_minor_currency_units(
            -refund_tx.amount,  # The amount is negative for refund transactions
            refund_tx.currency_id
        )

        payload = {
            'payment_id': self.hitpay_payment_id,
            'amount': amount_to_refund,
        }
        
        response_content = refund_tx.provider_id._hitpay_make_request(
            '/refund', payload=payload
        )

        _logger.info(
            "Hitpay refund request response for transaction with reference %s:\n%s",
            self.reference, pprint.pformat(response_content)
        )

        # Handle the refund request response
        self.hitpay_refund_id = response_content.get('id')
        self.hitpay_refund_createdat = response_content.get('created_at')
        self.hitpay_refund_amount = response_content.get('amount_refunded')
        self.hitpay_refund_currency = response_content.get('currency')

        self.provider_reference = self.hitpay_refund_id

        message = "Refund successful. Refund Reference Id: "+self.hitpay_refund_id+", "
        message += "Payment Id: "+self.hitpay_payment_id+", "
        message += "Amount Refunded: "+self.hitpay_refund_amount+", "
        message += "Payment Method: "+response_content.get('payment_method')+", "
        message += "Created At: "+ self.hitpay_refund_createdat

        self._set_done()
        self.env.ref('payment.cron_post_process_payment_tx')._trigger()

        return refund_tx