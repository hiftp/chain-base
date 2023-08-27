odoo.define('pl_curved_backend_theme.plAbstractController', function(require) {
    "use strict";

    var AbstractController = require('web.AbstractController');
    AbstractController.include({
        reload: async function(params={}, PlReloadAnotherView=true) {
            if (params.controllerState) {
                this.importState(params.controllerState);
                Object.assign(params, this.searchModel.get('query'));
            }
            return this.update(params, {}, PlReloadAnotherView);
        },
    });
});
