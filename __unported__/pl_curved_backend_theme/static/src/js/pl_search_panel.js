/** @odoo-module **/

const SearchPanel = require("web.searchPanel");
import { patch } from 'web.utils';

patch(SearchPanel.prototype, '/pl_curved_backend_theme/static/src/js/pl_search_panel.js', {
    _plSearchPanelClose(){
        $(".pl_search_panel").removeClass("show");
    }

});