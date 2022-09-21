odoo.define('search.bank.account.balance', function (require) {
    "use strict";

    let core = require('web.core');
    let _t = core._t;
    let QWeb = core.qweb;
    let Widget = require('web.Widget');
    let Model = require('web.Model');
    let InterfaceSearchBankAccountBalance = Widget.extend({
        events: {
            //按钮点击动作function
            "click #search": function (env) {
                let self = this;
                let s_type = self.$el.find('#s_type').val();
                let account_id = self.$el.find('#account_id').val();
                let external_id = self.$el.find('#external_id').val();
                if (s_type == '0') {
                    self.do_warn('警告', '请选择账户类型!');
                    return;
                }
                if (account_id == '0') {
                    self.do_warn('警告', '请选择查询账户!');
                    return;
                }
                //检查选择为银行账户时 银行账户必填
                if (s_type == '20009') {
                    if (external_id == '0') {
                        self.do_warn('警告', '请选择银行账户!');
                        return;
                    }
                }
                new Model('search.bank.account.balance').call('search_account_bal_new', [s_type, account_id, external_id])
                    .then(function (res) {
                        self.$el.find('#search_result').html(QWeb.render("SearchBankAccountBalanceLine", {
                            widget: self,
                            data: res,
                        }));
                        self.$el.find('#excel_title').html('查询结果');
                    });
            },
        },

        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.next_action = 'hr_attendance.hr_attendance_action_kiosk_mode';
        },

        start: function () {
            let self = this;
            self.$el.html(QWeb.render("SearchBankAccountBalance", {widget: self}));
            new Model('search.bank.account.balance').call('get_s_type', [])
                .then(function (result) {
                    let $options = '<option value="0">请选择</option>';
                    for (let i = 0; i < result.length; i++) {
                        $options += '<option value="' + result[i].number + '">' + result[i].name + '</option>';
                    }
                    self.$el.find('#s_type').html($options);
                });
            new Model('search.bank.account.balance').call('get_payment_account', [])
                .then(function (result) {
                    let $options = '<option value="0">请选择</option>';
                    for (let i = 0; i < result.length; i++) {
                        $options += '<option value="' + result[i].id + '">' + result[i].costomer_name + '</option>';
                    }
                    self.$el.find('#account_id').html($options);
                });
            new Model('search.bank.account.balance').call('get_bank_account', [])
                .then(function (result) {
                    let $options = '<option value="0">查询银行账户时必填</option>';
                    for (let i = 0; i < result.length; i++) {
                        $options += '<option value="' + result[i].id + '">' + result[i].name + '</option>';
                    }
                    self.$el.find('#external_id').html($options);
                });
            self.$el.find('#search_result').html(QWeb.render("SearchBankAccountBalanceLine", {
                            widget: self,
                            data: []
                        }));
        }

    });

    core.action_registry.add('search_bank_account_balance', InterfaceSearchBankAccountBalance);
    return InterfaceSearchBankAccountBalance;
});
