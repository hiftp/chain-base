odoo.define('search.abc.account.consistent', function (require) {
    "use strict";

    let core = require('web.core');
    let QWeb = core.qweb;
    let Widget = require('web.Widget');
    let Model = require('web.Model');
    let SearchAbcAccountConsistent = Widget.extend({
        events: {
            //按钮点击动作function
            "click #search": function (env) {
                let self = this;
                let account_id = self.$el.find('#account_id').val();
                if (account_id == '0') {
                    self.do_warn('警告', '请选择付款账户!');
                    return;
                }
                let DbAccNo = self.$el.find('#DbAccNo').val();
                let DbAccName = self.$el.find('#DbAccName').val();
                let Amt = self.$el.find('#Amt').val();
                self.$el.find('#excel_title').html('正在查询...');
                new Model('interface.abc.account.consistent').call('search_account_consistent', [account_id, DbAccNo, DbAccName, Amt])
                    .then(function (res) {
                        self.$el.find('#search_result').html(QWeb.render("SearchAbcAccountConsistentResult", {
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
            self.$el.html(QWeb.render("SearchAbcAccountConsistent", {widget: self}));
            new Model('find.abc.account.bal').call('get_account', [])
                .then(function (result) {
                    let $options = '<option value="0">请选择付款账户</option>';
                    for (let i = 0; i < result.length; i++) {
                        $options += '<option value="' + result[i].id + '">' + result[i].costomer_name + '</option>';
                    }
                    self.$el.find('#account_id').html($options);
                });
            self.$el.find('#search_result').html(QWeb.render("SearchAbcAccountConsistentResult", {
                widget: self,
                data: {}
            }));
        }

    });

    core.action_registry.add('find_account_consistent', SearchAbcAccountConsistent);
    return SearchAbcAccountConsistent;
});