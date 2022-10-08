/** @odoo-module */

import { ControlPanel } from "@web/search/control_panel/control_panel";
import { patch } from 'web.utils';
import Dialog from 'web.Dialog';
import core from 'web.core';
const { useListener } = require("web.custom_hoopl");
const _t = core._t;

patch(ControlPanel.prototype, 'pl_curved_backend_theme/static/src/js/Pl_controlpanel_view.js', {
    setup() {
      this._super();
      useListener( "click", ".reload_view", this._PlReloadView );
      },

    _PlReloadView: function() {
        location.reload(); //bug
    },

     _plActiveSearchFilter() {
        var pl_all_sections = this.searchMenus;
        var pl_result = [];
        if (pl_all_sections) {
            pl_all_sections.forEach((element,index)=>{
                if (element.type == "filter") {
                    var pl_display = false
                    element.values.forEach((values,index)=>{
                        if (values.checked) {
                            if (!pl_display)
                                pl_display = values.display_name;
                            else
                                pl_display += ', ' + values.display_name;
                        }
                    }
                    );
                    if (pl_display) {
                        pl_result.push({
                            icon: element.icon,
                            display_name: pl_display,
                        });
                    }
                }
                if (element.activeValueId) {
                    let pl_active_id = element.activeValueId;
                    element.values.forEach((values,index)=>{
                        if (values.id == pl_active_id) {
                            pl_result.push({
                                icon: element.icon,
                                display_name: values.display_name,
                            });
                        }
                    }
                    );
                }
            }
            );
        }
        return pl_result;
    },

    _plSearchFragmentOpen() {
        $(".pl-phone-filter-modal").addClass("show");
        $('div.pl-item-search-box').removeClass("d-none");
    },

    _plSearchFragmentClose() {
        $(".pl-phone-filter-modal").removeClass("show");
        $('div.pl-item-search-box').addClass("d-none");
    },

    _plSearchReset() {
        this.env.searchModel.clearQuery();
    },

    _plViewSwitcher(ev) {
        $(".o_cp_switch_buttons").removeClass("show");
        this.trigger("switch-view", {
            view_type: $(ev.currentTarget).attr("plView"),
        });
    },

    _plSearchPanelOpen() {
           $('.o_search_panel').toggle();
           if($('.o_search_panel').is(":visible")){
                $('button.pl-phone-category-btn i').removeClass('fa-filter');
                $('button.pl-phone-category-btn i').addClass('fa-arrow-left');
            }else{
            $('button.pl-phone-category-btn i').removeClass('fa-arrow-left');
                $('button.pl-phone-category-btn i').addClass('fa-filter');
                }
          // $('.o_search_panel').toggleClass('');

      //  $(".pl_search_panel").addClass("show");
//        $(".pl_search_panel").removeClass("none");
    },

    _plCheckMobileView() {
        if (screen.width > 1024)
            return false;
        return true;
    },

    _plCheckSearchPanel() {
        var pl_search_data = this.searchMenus;
        if (pl_search_data.length>0)
            return true;
        return false;
//        var a =this.__proto__.__proto__._plCheckSearchPanel;
//        console.log(a.pl_search_data);
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

    _plMobileViewSwitcher() {
        $(".o_cp_switch_buttons").toggleClass("show");
    },

    _onplFullScreen(ev) {
        var pl_window = document.documentElement;
        var pl_elem_class = ev.currentTarget.classList;
        if (window.innerHeight == screen.height) {
            if ($("button.pl_fullscreen").hasClass("fa-expand")) {
                alert(_t("Browser is in fullscreen mode."));
            } else {
                try {
                    pl_elem_class.remove("fa-compress");
                    pl_elem_class.add("fa-expand");
                    if (document.exitFullscreen) {
                        document.exitFullscreen();
                    } else if (document.webkitExitFullscreen) {
                        /* Safari */
                        document.webkitExitFullscreen();
                    } else if (document.msExitFullscreen) {
                        /* IE11 */
                        document.msExitFullscreen();
                    }
                } catch (err) {
                    alert(_t("Unable to perform this operation."));
                }
            }
        } else {
            pl_elem_class.remove("fa-expand");
            pl_elem_class.add("fa-compress");
            if (pl_window.requestFullscreen) {
                pl_window.requestFullscreen();
            } else if (pl_window.webkitRequestFullscreen) {
                /* Safari */
                pl_window.webkitRequestFullscreen();
            } else if (pl_window.msRequestFullscreen) {
                /* IE11 */
                pl_window.msRequestFullscreen();
            }
        }

        document.addEventListener("fullscreenchange", (event)=>{
            if (document.fullscreenElement) {
                $("button.pl_fullscreen").removeClass("fa-expand");
                $("button.pl_fullscreen").addClass("fa-compress");
            } else {
                $("button.pl_fullscreen").removeClass("fa-compress");
                $("button.pl_fullscreen").addClass("fa-expand");
            }
        });
    },

});


