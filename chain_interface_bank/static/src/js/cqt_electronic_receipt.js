odoo.define('o_electronic_receipt_tree_btn', function (require) {
    "use strict";
    var core = require('web.core');
    var ListView = require('web.ListView');
    var Model = require('web.Model');
    var session = require('web.session');
    var ajax = require("web.ajax");
    var Dialog = require('web.Dialog');

    var QWeb = core.qweb;
    var _t = core._t;


    /**
     * 查询(财企通)电子回单
     */
    function execute_open_action() {
        let save_data = function () {
            let custNo = $("#custNo").val()
            let custName = $("#custName").val()
            let slipId = $("#slipId").val()
            let slipNo = $("#slipNo").val()
            let startDate = $("#startDate").val()
            let endDate = $("#endDate").val()
            new Model('interface.bank.electronic.receipt.result').call('search_electronic_receipt_result', [custNo, custName, slipId, slipNo, startDate, endDate]).then(function (result) {
                if (result.state) {
                    new Dialog.confirm(this, result.msg, {
                        'title': '结果提示'
                    });
                }
            });
        };
        new Model("interface.bank.electronic.receipt.result").call('get_state').then(function (result) {
            new Dialog(this, {
                title: "查询(财企通)电子回单",
                size: 'medium',
                buttons: [
                    {
                        text: "开始查询",
                        classes: 'btn-primary',
                        close: true,
                        click: save_data
                    }, {
                        text: "取消查询",
                        close: true
                    }
                ],
                $content: $(QWeb.render('InterfaceBankElectronicReceipt', {widget: this, data: []}))
            }).open();
        });
    }

    /**
     * 通过添加事件侦听器来扩展ListView的render_buttons函数
     * 在导入按钮上。
     * @return {jQuery}渲染的按钮
     */
    ListView.include({
        render_buttons: function () {
            let add_button = false;
            if (!this.$buttons) {
                add_button = true;
            }
            this._super.apply(this, arguments);
            if (add_button) {
                this.$buttons.on('click', '.o_electronic_receipt', execute_open_action.bind(this));
            }
        }
    });
});