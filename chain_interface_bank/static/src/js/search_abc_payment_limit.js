odoo.define('search.abc.payment.limit', function (require) {
    "use strict";

    let core = require('web.core');
    let QWeb = core.qweb;
    let Widget = require('web.Widget');
    let Model = require('web.Model');
    let InterfaceAbcAbnormalTransaction = Widget.extend({
        events: {
            //按钮点击动作function
            "click #search": function (env) {
                let self = this;
                let account_id = self.$el.find('#account_id').val();
                let currency_id = self.$el.find('#currency_id').val();
                if (account_id == '0') {
                    self.do_warn('警告', '请选择付款账户!');
                    return;
                }
                if (currency_id == '0') {
                    self.do_warn('警告', '请选择交易币种!');
                    return;
                }
                self.$el.find('#excel_title').html('正在查询...');
                new Model('interface.abc.payment.limit').call('search_payment_limit', [account_id, currency_id])
                    .then(function (res) {
                        self.$el.find('#search_result').html(QWeb.render("SearchAbcBankPaymentLimitResult", {
                            widget: self,
                            data: res,
                        }));
                        self.$el.find('#excel_title').html('查询结束!');
                    });
            },
        },

        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.next_action = 'hr_attendance.hr_attendance_action_kiosk_mode';
        },

        start: function () {
            let self = this;
            self.$el.html(QWeb.render("SearchAbcBankPaymentLimit", {widget: self}));
            new Model('find.abc.account.bal').call('get_account', [])
                .then(function (result) {
                    let $options = '<option value="0">请选择</option>';
                    for (let i = 0; i < result.length; i++) {
                        $options += '<option value="' + result[i].id + '">' + result[i].costomer_name + '</option>';
                    }
                    self.$el.find('#account_id').html($options);
                });
            new Model('find.abc.account.bal').call('get_currency', [])
                .then(function (result) {
                    let $options = '<option value="0">请选择</option>';
                    for (let i = 0; i < result.length; i++) {
                        $options += '<option value="' + result[i].id + '">' + result[i].name + '</option>';
                    }
                    self.$el.find('#currency_id').html($options);
                });
            self.$el.find('#search_result').html(QWeb.render("SearchAbcBankPaymentLimitResult", {
                widget: self,
                data: {}
            }));
        }

    });

    core.action_registry.add('find_abc_payment_limit', InterfaceAbcAbnormalTransaction);
    return InterfaceAbcAbnormalTransaction;
});