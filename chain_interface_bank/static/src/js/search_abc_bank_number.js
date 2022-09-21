odoo.define('interface.abc.search.bank.number', function (require) {
    "use strict";

    let core = require('web.core');
    let QWeb = core.qweb;
    let Widget = require('web.Widget');
    let Model = require('web.Model');
    let InterfaceAbcSearchBankNumber = Widget.extend({
        events: {
            //按钮点击动作function
            "click #search": function (env) {
                let self = this;
                let bank_name = self.$el.find('#bank_name').val();
                let account_id = self.$el.find('#account_id').val();
                let bank_id = self.$el.find('#bank_id').val();
                if (account_id == '0') {
                    self.do_warn('警告', '请选择账户!');
                    return;
                }
                if (bank_id == '0') {
                    self.do_warn('警告', '请正确选择行别!');
                    return;
                }
                self.$el.find('#excel_title').html('正在查询...');
                new Model('interface.abc.bank.number').call('search_bank_number', [account_id, bank_id, bank_name])
                    .then(function (res) {
                        self.$el.find('#search_result').html(QWeb.render("InterfaceAbcSearchBankNumberLine", {
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
            self.$el.html(QWeb.render("InterfaceAbcSearchBankNumber", {widget: self}));
            new Model('find.abc.account.bal').call('get_account', [])
                .then(function (result) {
                    let $options = '<option value="0">请选择</option>';
                    for (let i = 0; i < result.length; i++) {
                        $options += '<option value="' + result[i].id + '">' + result[i].costomer_name + '</option>';
                    }
                    self.$el.find('#account_id').html($options);
                });
            new Model('interface.abc.bank.number').call('get_abc_bank', [])
                .then(function (result) {
                    let $options = '<option value="0">请选择</option>';
                    for (let i = 0; i < result.length; i++) {
                        $options += '<option value="' + result[i].id + '">' + result[i].name + '</option>';
                    }
                    self.$el.find('#bank_id').html($options);
                });
            self.$el.find('#search_result').html(QWeb.render("InterfaceAbcSearchBankNumberLine", {
                widget: self,
                data: []
            }));
        }

    });

    core.action_registry.add('find_abc_bank_number', InterfaceAbcSearchBankNumber);
    return InterfaceAbcSearchBankNumber;
});