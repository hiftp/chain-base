odoo.define('pl_curved_backend_theme.pl_graph_controller_inherit', function(require) {
    "use strict";
    var pl_graph_controller = require('web.GraphController');
    var session = require("web.session");

    pl_graph_controller.include({
        events: _.extend({}, pl_graph_controller.prototype.events, {
            "click button.reload_view": "_PlReloadView",
        }),

        _PlReloadView: function() {
            this.reload();
        },

});
});