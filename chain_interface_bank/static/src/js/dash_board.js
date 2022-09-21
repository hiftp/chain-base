odoo.define('interface.bank.dashboard', function (require) {
    "use strict";

    let core = require('web.core');
    let _t = core._t;
    let QWeb = core.qweb;
    let Widget = require('web.Widget');
    let Model = require('web.Model');
    let InterfaceBankDashboard = Widget.extend({

        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.next_action = 'hr_attendance.hr_attendance_action_kiosk_mode';
        },

        start: function () {
            let self = this;
            self.$el.html(QWeb.render("InterfaceBankDashBoard", {widget: self}));
            new Model('interface.bank.payment').call('get_today_pay_money', [])
				.then(function (result) {
					self.$el.find('#today_money').html(result['today_money'].toFixed(2));
					self.$el.find('#payment_len').html(result['payment_len']);
				});
            new Model('interface.bank.payment').call('get_new_payment', [])
				.then(function (result) {
                    self.$el.find('#new_payment').html(QWeb.render("InterfaceBankDashBoardNewPayment", {
                        widget: self,
                        data: result,
                    }));
				});
            new Model('interface.bank.payment').call('get_payment_result', [])
				.then(function (result) {
                    self.$el.find('#payment_result').html(QWeb.render("InterfaceBankDashBoardPaymentResult", {
                        widget: self,
                        data: result,
                    }));
				});
        }

    });

    core.action_registry.add('interface_dash_board', InterfaceBankDashboard);
    return InterfaceBankDashboard;
});
