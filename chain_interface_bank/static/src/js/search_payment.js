odoo.define('interface_bank.payment.result', function (require) {
    "use strict";

    let core = require('web.core');
    let _t = core._t;
    let QWeb = core.qweb;
    var Widget = require('web.Widget');
    var Model = require('web.Model');
    var InterfaceBankSearchPaymentBackend = Widget.extend({
        events: {
            //按钮点击动作function
            "click #search": function (env) {
                let self = this;
                let from_number = self.$el.find('#payment_from_number').val();
                if (from_number == null || from_number == undefined || from_number == ''){
                    self.do_warn('警告', '付款单据编号不能为空!');
                    return false;
                }
                this.search_payment_result(from_number);
                // self.$el.find('#payment_from_number').val('');
            },
        },

        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.next_action = 'hr_attendance.hr_attendance_action_kiosk_mode';
        },

        start: function () {
            let self = this;
            self.$el.html(QWeb.render("InterfaceBankSearchPayment", {widget: self}));
        },

        search_payment_result: function (payment_from_number) {
            let self = this;
            new Model('interface.search.payment.res').call('search_payment_result', [payment_from_number])
                .then(function (res) {
                    self.$el.find('tbody').html(QWeb.render("InterfaceBankSearchPaymentResult", {
                        widget: self,
                        data: res,
                    }));
                    self.$el.find('#excel_title').html('查询结果');
                });
        }

    });

    core.action_registry.add('search_payment_result', InterfaceBankSearchPaymentBackend);
    return InterfaceBankSearchPaymentBackend;
});
