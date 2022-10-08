/** @odoo-module */

var { SearchBar } = require("@web/search/search_bar/search_bar");
import { patch } from 'web.utils';
import Dialog from 'web.Dialog';
import core from 'web.core';
const { useListener } = require("web.custom_hoopl");
const _t = core._t;

patch(SearchBar.prototype, 'pl_curved_backend_theme/static/src/js/Pl_searchbar.js', {

    _plSearchFragmentOpen() {
        $(".pl-phone-filter-modal").addClass("show");
        $('div.pl-item-search-box').removeClass("d-none");
    },

    _plSearchButtonOpen() {
        $(".pl_search_responsive").addClass("show");
        // Hide breadcrumb text and search icon.
        $(".o_cp_top_left .breadcrumb-item").addClass("d-none");
        $(".o_cp_top_right .pl-phone-sr-btn").addClass("d-none");
    },

    _plSearchButtonClose() {
        $(".pl_search_responsive").removeClass("show");
        $(".o_cp_top_left .breadcrumb-item").removeClass("d-none");
        $(".o_cp_top_right .pl-phone-sr-btn").removeClass("d-none");
    },


});


