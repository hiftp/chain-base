odoo.define('pl_curved_backend_theme.pl_list_controller', function(require) {
    "use strict";
    var pl_list_controller = require('web.ListController');
    var session = require("web.session");

    pl_list_controller.include({
        events: _.extend({}, pl_list_controller.prototype.events, {
            "click .reload_list_view": "_PlReloadView",
        }),

//        _PlReloadFormController: function() {
//            var form_controller = Object.keys(this.getParent().controllers).filter(x=>(this.getParent().controllers[x] && this.getParent().controllers[x].viewType == 'form'))
//            if (form_controller && form_controller.length) {
//                this.getParent().controllers[form_controller[0]].widget.reload({}, false);
//            }
//        },

        _PlReloadView: function() {
            this.reload();
        },

//        _onDeletedRecords: function() {
//            var state = this.model.get(this.handle, {
//                raw: true
//            });
//            var valid_records = _.map(state.data, function(x) {
//                return x.res_id
//            })
//            var form_controller = Object.keys(this.getParent().controllers).filter(x=>(this.getParent().controllers[x] && this.getParent().controllers[x].viewType == 'form'))
//            var is_records = true
//            if (form_controller && form_controller.length) {
//                var form_widget = this.getParent().controllers[form_controller[0]].widget
//                var form_state = form_widget.model.get(form_widget.handle, {
//                    raw: true
//                })
//                if (form_state && form_state.res_id && !valid_records.includes(form_state.res_id))
//                    is_records = false
//
//            }
//
//            if (!state.data.length || !is_records) {
//                this.trigger_up('history_back');
//            } else {
//                this._super.apply(this, arguments);
//            }
//        },
//        update: async function(params, options, reload_controller=true) {
//            this.mode = params.mode || this.mode;
//            var res = this._super(params, options);
//            if (reload_controller && session['pl_split_view'] && session['pl_split_view'] != 'no_split') {
//                this._PlReloadFormController();
//            }
//            return res;
//        },
//
    });

});
