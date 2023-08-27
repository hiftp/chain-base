odoo.define('pl_curved_backend_theme.pl_kanban_controller_inherit', function(require) {
    "use strict";
    var pl_kanban_controller = require('web.KanbanController');
    var session = require("web.session");

    pl_kanban_controller.include({
        events: _.extend({}, pl_kanban_controller.prototype.events, {
            "click button.reload_view": "_PlReloadView",
        }),

        _PlReloadView: function() {
            this.reload();
        },

});
});