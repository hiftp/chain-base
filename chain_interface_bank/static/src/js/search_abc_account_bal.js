odoo.define('search.abc.bank.account.balance', function (require) {
    "use strict";

    let core = require('web.core');
    let _t = core._t;
    let QWeb = core.qweb;
    let Widget = require('web.Widget');
    let Model = require('web.Model');
    let InterfaceSearchABCBankAccountBalance = Widget.extend({
        events: {
            //按钮点击动作function
            "click #search": function (env) {
                let self = this;
                let account_id = self.$el.find('#account_id').val();
                let currency_id = self.$el.find('#currency_id').val();
                if (account_id == '0') {
                    self.do_warn('警告', '请选择账户!');
                    return;
                }
                if (currency_id == '0') {
                    self.do_warn('警告', '请选择交易币种!');
                    return;
                }
                self.$el.find('#excel_title').html('正在查询...');
                new Model('find.abc.account.bal').call('start_find_account_bal', [account_id, currency_id])
                    .then(function (res) {
                        self.$el.find('#search_result').html(QWeb.render("SearchABCBankAccountBalanceLine", {
                            widget: self,
                            data: res,
                        }));
                        self.$el.find('#excel_title').html('查询成功!');
                    });
            },
        },

        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.next_action = 'hr_attendance.hr_attendance_action_kiosk_mode';
        },

        start: function () {
            let self = this;
            self.$el.html(QWeb.render("SearchABCBankAccountBalance", {widget: self}));
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
            self.$el.find('#search_result').html(QWeb.render("SearchABCBankAccountBalanceLine", {
                            widget: self,
                            data: {
                                'DbAccName': '******',
                                'Bal': '0.00',
                                'AvailBal': '0.00',
                                'AccType': '0',
                                'AccSts': '0.00',
                                'LastBal': '0.00',
                                'FrzAmt': '0.00',
                                'FrzBal': '0.00',
                                'ValUDLmt': '0.00',
                                'ValMonthLmt': '0.00',
                                'ValDayLmt': '0.00',
                                'LastAvailBal': '0.00',
                                'DbAccNo': '******',
                                'costomer_number': '******',
                            }
                        }));
        }

    });

    core.action_registry.add('find_abc_account_bal', InterfaceSearchABCBankAccountBalance);
    return InterfaceSearchABCBankAccountBalance;
});