odoo.define('interface.abc.search.file.detail', function (require) {
    "use strict";

    let core = require('web.core');
    let QWeb = core.qweb;
    let Widget = require('web.Widget');
    let Model = require('web.Model');
    let InterfaceABCSearchWagesResult = Widget.extend({
        events: {
            //按钮点击动作function
            "click #search": function (env) {
                let self = this;
                let form_code = self.$el.find('#form_code').val();
                let account_id = self.$el.find('#account_id').val();
                if (account_id == '0') {
                    self.do_warn('警告', '请选择账户!');
                    return;
                }
                self.$el.find('#excel_title').html('正在查询...');
                new Model('interface.abc.search.file.detail').call('search_file_detail', [account_id, form_code])
                    .then(function (res) {
                        self.$el.find('#search_result').html(QWeb.render("InterfaceABCSearchFileDetailLine", {
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
            self.$el.html(QWeb.render("InterfaceABCSearchFileDetail", {widget: self}));
            new Model('find.abc.account.bal').call('get_account', [])
                .then(function (result) {
                    let $options = '<option value="0">请选择</option>';
                    for (let i = 0; i < result.length; i++) {
                        $options += '<option value="' + result[i].id + '">' + result[i].costomer_name + '</option>';
                    }
                    self.$el.find('#account_id').html($options);
                });
            self.$el.find('#search_result').html(QWeb.render("InterfaceABCSearchFileDetailLine", {
                widget: self,
                data: []
            }));
        }

    });

    core.action_registry.add('search_abc_file_detail', InterfaceABCSearchWagesResult);
    return InterfaceABCSearchWagesResult;
});