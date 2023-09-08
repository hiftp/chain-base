odoo.define('organisation.checkout_form', require => {
    'use strict';

    const publicWidget = require('web.public.widget');

    const paymentFormMixin = require('payment.payment_form_mixin');
    const PaymentCheckoutForm = require('payment.checkout_form');
    var rpc = require('web.rpc');
    var session = require('web.session');
    const ajax = require('web.ajax');

    PaymentCheckoutForm.include({
        _onClickPay: async function (ev) {
            var self = this;
            var check = document.getElementById('check').checked;
            console.log(check);
            if(check){
                var email = document.getElementById('email').value;
                if(email){
                    self._super(...arguments);
                    await ajax.jsonRpc("/partner/update", 'call', {
                        'email' : email,
                    }).then(function (result) {
                    })
                }
                else{
                    alert("Please enter the email")
                }
            }
            else{
                self._super(...arguments);
            }
        },
    });
    return PaymentCheckoutForm;
});