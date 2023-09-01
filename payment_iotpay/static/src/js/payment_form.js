odoo.define('payment_iotpay.payment_form', require => {
    'use strict';

    const checkoutForm = require('payment.checkout_form');
    const manageForm = require('payment.manage_form');

    const paymentIotpayMixin = {

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * Simulate a feedback from a payment provider and redirect the customer to the status page.
         *
         * @override method from payment.payment_form_mixin
         * @private
         * @param {string} provider - The provider of the acquirer
         * @param {number} acquirerId - The id of the acquirer handling the transaction
         * @param {object} processingValues - The processing values of the transaction
         * @return {Promise}
         */
        _processDirectPayment: function (provider, acquirerId, processingValues) {
            if (provider !== 'iotpay') {
                return this._super(...arguments);
            }
            if(processingValues.retCode === 'SUCCESS'){
                window.location = processingValues.iotpay_url;
            }else{
            	  alert("IoTPay Error: " + processingValues.retMsg);
            }
        },

        _prepareInlineForm: function (provider, paymentOptionId, flow) {
            if (provider !== 'iotpay') {
                return this._super(...arguments);
            } else if (flow === 'token') {
                return Promise.resolve();
            }
            this._setPaymentFlow('direct');
            return Promise.resolve()
        },
    };
    checkoutForm.include(paymentIotpayMixin);
    manageForm.include(paymentIotpayMixin);
});
