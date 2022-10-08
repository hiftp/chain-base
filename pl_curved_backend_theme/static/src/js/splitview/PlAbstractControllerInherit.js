odoo.define('pl_curved_backend_theme.PlAbstractControllerInherit', function (require) {
"use strict";

var AbstractController = require('web.AbstractController');
const { ComponentWrapper } = require('web.OwlCompatibility');
var session = require("web.session");

AbstractController.include({
    start: async function () {
        // Overrrided to add split view classes
        var res = this._super.apply(this, arguments);
        if(session['pl_split_view'] && session['pl_split_view'] != 'no_split'){
            if(this.viewType == 'form'){
                this.$el.addClass('pl_splitted_page');
            }else if(this.viewType == 'list'){
                $('body').removeClass('pl_splitter horizontal-split');
            }
        }
        return res
    },
});
return AbstractController;
});