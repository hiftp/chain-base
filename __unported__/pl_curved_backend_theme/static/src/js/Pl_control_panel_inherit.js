odoo.define('pl_curved_backend_theme.Pl_control_panel_inherit.js', function (require) {
    "use strict";

   const ControlPanel = require('web.ControlPanel');
   var session = require("web.session");
   const { patch } = require('web.utils');


   // Overrided to add a method which will return the flag that wether a user is using the system through mobile device or pc

   patch(ControlPanel.prototype, 'pl_curved_backend_theme.Pl_control_panel_inherit.js', {
        mounted() {
            this._super();
            this.props['pl_breadcrumb_style'] = session['pl_breadcrumb_style'];
            // add breadcrumb class
            $('ol.pl_custom_breadcrumb').addClass(session['pl_breadcrumb_style']);
        },

        plIsMobileDevice() {
            return this.env.device.isMobile;
        },
   });

});


