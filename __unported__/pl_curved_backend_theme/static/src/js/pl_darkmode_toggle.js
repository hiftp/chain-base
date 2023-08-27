odoo.define("pl_curved_backend_theme.Pl_darkmode_toggle", function(require) {
    "use strict";

    var SystrayMenu = require("web.SystrayMenu");
    var Widget = require("web.Widget");
    var ajax = require("web.ajax");
    var session = require("web.session");
    var quick_settings = require("pl_curved_backend_theme.pl_quick_settings_widget")
    var widgetRegistry = require("web.widget_registry");
    var core = require("web.core");
    var _t = core._t;
//    var mail_activity_menu = require("mail.systray.ActivityMenu");
//    var mail_message_menu = require("mail/static/src/widgets/messaging_menu/messaging_menu.js");

//    mail_message_menu.include({
//      sequence: 5,
//    });
//    mail_activity_menu.include({
//      sequence: 4,
//    });
    var pl_toggle_switch = Widget.extend({
        template: "pl_toggle_switch",
        events: {
            "change input#pl_menubar_dark_mode": "_onInputChange",
        },

        sequence: 60,

        willStart: async function() {
            const _super = this._super.bind(this);

            const data = await this._rpc({
                route: "/render/theme/view/data",
                params: {
                    pl_setting_scope: "User"
                },
            });
            this.data = data;
            return _super;
        },

        _onInputChange: function(ev) {
            var self = this;
            var args = {};
            var _value = ev.target.checked;

            args[$(ev.target).data('name')] = _value
            if(! _value && this.data.pl_auto_dark_mode){
                $(ev.target).prop('checked', true);
                this.displayNotification({
                        title: _t("Error"),
                        message: _t("Please first turn off the auto dark mode to use this feature!")
                    });
//                this.do_warn(
//                      _t("Error"),
//                      _t("Please first turn off the auto dark mode to use this feature!")
//                );
                return;
            }
            if (_value) {
                // Show auto dark mode.
                $("div#pl_auto_dark_mode_div").css("display", "block");
            } else {
                // Hide.
                $("div#pl_auto_dark_mode_div").css("display", "none");
            }

            ajax.jsonRpc("/save/theme/settings", "call", {
                pl_unsaved_setting: args,
                pl_origin_scope: "user",
            }).then(function() {
                self._PlInitiateModeChangeProcess(_value)
            });

        },

        _PlInitiateModeChangeProcess: function(_value) {
            var self = this;
            var pl_apply_dark_mode = _value;
            $('#pl_dark_mode').prop('checked', _value)
            if (this.data.pl_auto_dark_mode && this.data.pl_sun_time_info && pl_apply_dark_mode) {
                // Check theme light/dark mode based on sun time.
                var pl_current_datetime = new Date();
                var pl_sunrise_datetime = new Date("01 Jan 2000 " + this.data.pl_sun_time_info.sunrise);
                var pl_sunset_datetime = new Date("01 Jan 2000 " + this.data.pl_sun_time_info.sunset);

                //          self.trigger_up("plCompareTime", {
                //                'pl_sunrise_datetime': pl_sunrise_datetime,
                //                'pl_sunset_datetime': pl_sunset_datetime,
                //                'pl_current_datetime': pl_current_datetime
                //            })
                if (self._plCompareTime(pl_sunrise_datetime, pl_sunset_datetime, pl_current_datetime)) {
                    pl_apply_dark_mode = false;
                }
            }
            if (pl_apply_dark_mode)
                $("html").attr("data-color-mode", "pl-dark");
            else
                $("html").attr("data-color-mode", "pl-light");
            session.pl_current_color_mode = $("html").attr("data-color-mode");
            var quick_settings_obj = new quick_settings();
            self._plManageCurrentColorTheme(quick_settings_obj._plGetHeaderIconColor(session.pl_color_theme["body-background"]));
            if (document.body.classList.contains("pl_appsmenu_active"))
                self.trigger_up("pl_manage_drawer", {
                    drawer_status: 'open'
                });
        },

        /*
       * Function to compare two datetime based on times
       * return true if pl_datetime_1 < pl_datetime, otherwise false.
       */
        _plCompareTime: function(pl_sunrise_datetime, pl_sunset_datetime, pl_current_datetime) {
            var pl_hours = pl_current_datetime.getHours();
            var pl_minutes = pl_current_datetime.getMinutes();
            var pl_seconds = pl_current_datetime.getSeconds();
            var pl_curr_time = new Date("01 Jan 2000 " + pl_hours + ":" + pl_minutes + ":" + pl_seconds);
            if (pl_sunrise_datetime < pl_curr_time && pl_curr_time < pl_sunset_datetime) {
                return true;
            }
            return false;
        },

        _plManageCurrentColorTheme(background) {
            var pl_current_theme = session.pl_color_theme;
            var pl_header_icon_clr = background;

            // Change header icons color for light and when body color is dark.
            if (session.pl_current_color_mode == "pl-light" && pl_header_icon_clr == "white") {
                session.pl_color_theme.pl_header_icon_clr = pl_header_icon_clr;
                // Change header font icons to white.
                $("div.o_menu_systray").addClass("pl_color_theme_dark_header");
                $(".o_main_navbar button.phone-menu-btn").addClass("pl_color_theme_dark_header");
                $(".pl_left_sidebar_panel .pl_app_sidebar .inner-sidebar button.phone-menu-btn").addClass("pl_color_theme_dark_header");
            } else if (session.pl_current_color_mode == "pl-dark" && pl_header_icon_clr == "white") {
                $("div.o_menu_systray").removeClass("pl_color_theme_dark_header");
                $(".o_main_navbar button.phone-menu-btn").removeClass("pl_color_theme_dark_header");
                $(".pl_left_sidebar_panel .pl_app_sidebar .inner-sidebar button.phone-menu-btn").removeClass("pl_color_theme_dark_header");

            }

            // Control view bg color.
            if (session.pl_current_color_mode == "pl-light" && !pl_current_theme.default_theme) {
                document.body.style.setProperty("--pl-main-control-bg", "#FFFFFF");
                if (pl_header_icon_clr == "white") {
                    document.body.style.setProperty("--app-drawar", "#FFFFFF");
                }
            } else if (session.pl_current_color_mode == "pl-dark") {
                document.body.style.removeProperty("--pl-main-control-bg");
                document.body.style.removeProperty("--app-drawar");
            }

            if (pl_current_theme.primary) {
                document.body.style.setProperty("--primary", pl_current_theme.primary);
                if (pl_current_theme["body-background"] == pl_current_theme.primary && session.pl_current_color_mode == "pl-light") {
                    document.body.style.setProperty("--nav-primary", "#ffffff");
                } else {
                    document.body.style.removeProperty("--nav-primary");
                    document.body.style.setProperty("--nav-primary", pl_current_theme.primary);
                }
            }

            if (pl_current_theme["primary-btn"]) {
                document.body.style.setProperty("--primary-btn", pl_current_theme["primary-btn"]);
            }

            if (pl_current_theme["tooltip-heading-bg"]) {
                document.body.style.setProperty("--tooltip-heading-bg", pl_current_theme["tooltip-heading-bg"]);
            }

            if (pl_current_theme["link-color"]) {
                document.body.style.setProperty("--link-color", pl_current_theme["link-color"]);
            }

            if (pl_current_theme["heading-color"]) {
                document.body.style.setProperty("--heading-color", pl_current_theme["heading-color"]);
            }

            if (session.pl_current_color_mode == "pl-light") {
                if (pl_current_theme["body-background"]) {
                    document.body.style.setProperty("--body-background", pl_current_theme["body-background"]);
                }

                // Only apply this variable if not background image is active.
                if (!this.data.pl_body_background_image_enable) {
                    if (pl_current_theme["nav-link-color"]) {
                        document.body.style.setProperty("--nav-link-color", pl_current_theme["nav-link-color"]);
                    }
                    if (pl_current_theme["pl-over-link"]) {
                        document.body.style.setProperty("--pl-over-link", pl_current_theme["pl-over-link"]);
                    }
                } else if (this.data.pl_body_background_image_enable && !this.data.pl_body_background_img.filter((pl_data)=>{
                    return pl_data.pl_active == true;
                }
                ).length) {
                    if (pl_current_theme["nav-link-color"]) {
                        document.body.style.setProperty("--nav-link-color", pl_current_theme["nav-link-color"]);
                    }
                    if (pl_current_theme["pl-over-link"]) {
                        document.body.style.setProperty("--pl-over-link", pl_current_theme["pl-over-link"]);
                    }
                } else {
                    $("div.o_menu_systray").removeClass("pl_color_theme_dark_header");
                    $(".o_main_navbar button.phone-menu-btn").removeClass("pl_color_theme_dark_header");
                    $(".pl_left_sidebar_panel .pl_app_sidebar .inner-sidebar button.phone-menu-btn").removeClass("pl_color_theme_dark_header");
                }

                if (pl_current_theme["tab-bg"]) {
                    document.body.style.setProperty("--tab-bg", pl_current_theme["tab-bg"]);
                }
            } else {
                // Make Dark theme
                if (pl_current_theme["body-background"]) {
                    document.body.style.removeProperty("--body-background");
                }

                // Only apply this variable if not background image is active.
                if (!this.data.pl_body_background_image_enable) {
                    if (pl_current_theme["nav-link-color"]) {
                        document.body.style.removeProperty("--nav-link-color");
                    }
                    if (pl_current_theme["pl-over-link"]) {
                        document.body.style.removeProperty("--pl-over-link");
                    }
                } else if (this.data.pl_body_background_image_enable && !this.data.pl_body_background_img.filter((pl_data)=>{
                    return pl_data.pl_active == true;
                }
                ).length) {
                    if (pl_current_theme["nav-link-color"]) {
                        document.body.style.removeProperty("--nav-link-color");
                    }
                    if (pl_current_theme["pl-over-link"]) {
                        document.body.style.removeProperty("--pl-over-link");
                    }
                }
                if (pl_current_theme["tab-bg"]) {
                    document.body.style.removeProperty("--tab-bg");
                }
            }
        },
    });
    SystrayMenu.Items.push(pl_toggle_switch);
    return pl_toggle_switch;
});
