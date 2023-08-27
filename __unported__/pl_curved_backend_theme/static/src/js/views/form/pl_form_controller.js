odoo.define('pl_curved_backend_theme.pl_form_controller', function(require) {
    "use strict";
    var pl_form_controller = require('web.FormController');
    var session = require("web.session");

    pl_form_controller.include({
        events: _.extend({}, pl_form_controller.prototype.events, {
            "click button.reload_form_view": "_PlReloadView",
        }),

        _PlReloadView: function() {
            this.reload();
        },

//        _PlReloadListController: function() {
//            var list_controller = Object.keys(this.getParent().controllers).filter(x=>(this.getParent().controllers[x] && this.getParent().controllers[x].viewType == 'list'))
//            if (list_controller && list_controller.length) {
//                this.getParent().controllers[list_controller[0]].widget.reload({}, false);
//            }
//        },
//
//        update: async function(params, options, reload_controller=true) {
//            this.mode = params.mode || this.mode;
//            var res = this._super(params, options);
//            if (reload_controller && session['pl_split_view'] && session['pl_split_view'] != 'no_split') {
//                this._PlReloadListController();
//            }
//            return res;
//        },

    });

});
