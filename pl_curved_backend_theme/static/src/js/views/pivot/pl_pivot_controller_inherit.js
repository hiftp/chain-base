odoo.define('pl_curved_backend_theme.pl_pivot_controller_inherit', function(require) {
    "use strict";
    var pl_pivot_controller = require('web.PivotController');
    var session = require("web.session");

    pl_pivot_controller.include({
        events: _.extend({}, pl_pivot_controller.prototype.events, {
            "click button.reload_view": "_PlReloadView",
        }),

        _PlReloadView: function() {
            this.reload();
        },

});
});