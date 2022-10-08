odoo.define("pl_curved_backend_theme.pl_quick_settings_widget", function(require) {
    "use strict";

    var core = require("web.core");
    var qweb = core.qweb;
    var ajax = require("web.ajax");
    var SystrayMenu = require("web.SystrayMenu");
    var Widget = require("web.Widget");
    var PlSwitchCompanyMenu = require("@web/webclient/switch_company_menu/switch_company_menu");
    const { systrayItem , SwitchCompanyMenu } = require("@web/webclient/switch_company_menu/switch_company_menu");
    const { registry } = require("@web/core/registry");
    const { patch } = require('web.utils');
    var session = require("web.session");
    var web_time = require("web.time");
    var utils = require("web.utils");
    var ajax = require("web.ajax");
    var Dialog = require("web.Dialog");
    var _t = core._t;

    // Change the sequence of Switch company Menu
    registry.category("systray").content.SwitchCompanyMenu[0] = 2;

    var PlQuickSettings = Widget.extend({
        template: "pl_quick_settings",

        file_type_magic_word: {
            "/": "jpg",
            R: "gif",
            i: "png",
            P: "svg+xml",
        },

        events: {
            "click .btn-global-settings": "_plGlobalSettings",
            "click .pl_user_settings": "_plUserSettings",
            "click .pl-dropdown-close": "_plHideUserSettings",
            "click .pl_body_background_del, .pl_drawer_background_del": "_plDelBackgroundImage",
            "change input": "_onInputChange",
            "click button.pl_setting_save": "_plSettingSave",
            "click button.pl_setting_cancel": "_plSettingCancel",
            "click button#pl_add_custom_theme_user": "_plUserCustomThemeAdd",
            "click .pl_background_default": "_plBackgroundDefault",
            "click .pl_drawer_background_default": "_plDrawerBackgroundDefault",
            "click .pl_user_theme_edit": "_plUserThemeEdit",
            "click .pl_user_theme_delete": "_plUserThemeDelete",
            "click .pl_theme_edit_cancel": "_plUserThemeCancel",
            "click .pl_theme_edit_update": "_plUserThemeUpdate",
            "click .pl_new_theme_save": "_plUserThemeSave",
            "click .pl_user_reset_color_theme": "_plColorThemeResetToDefault",
        },
        // force this item to be the first one to the left of the UserMenu in the systray
        sequence: 1,
        /**
       * @override
       **/
        init: function() {
            this._super.apply(this, arguments);
            // Prevent it to call quickly again again
            this._onSwitchCompanyClick = _.debounce(this._onSwitchCompanyClick, 1500, true);
            this.data = false;
            this.pl_dirty_data = {}
            this.pl_unsaved_setting = {};
            this.pl_user_theme_fields = ["pl_body_background", "pl_menu", "pl_menu_hover", "pl_button", "pl_border", "pl_heading", "pl_link", "pl_primary_color", "pl_tooltip", ];
        },
        /**
       * @override
       **/
        willStart: async function() {
            const _super = this._super.bind(this);
            const data = await this._rpc({
                route: "/render/theme/view/data",
                params: {
                    pl_setting_scope: "User"
                },
            });
            this.data = data;

            // Applying color theme
            const pl_current_theme = await this._rpc({
                route: "/pl_curved_backend_theme/getTheme",
                params: {},
            });
            // Add current theme info on color theme.
            session.pl_color_theme = pl_current_theme;

            // Update configuration values to session for further use.
            session.pl_curved_backend_theme_data = data;

            // Apply css based on the scopes.
            const pl_dynamic_css = await this._rpc({
                model: "pl.global.config",
                method: "pl_get_value_from_scope",
                args: [["pl_button_style", "pl_theme_style", "pl_tab_style", "pl_font_style", "pl_separator_style", "pl_checkbox_style", "pl_font_size", "pl_chatter", "pl_radio_button_style", "pl_popup_animation_style", ], ],
            });

            const pl_drawer_details = await this._rpc({
                model: "pl.global.config",
                method: "get_body_background",
                args: [["pl_app_drawer_background"]],
            });
            if (pl_drawer_details && pl_drawer_details.pl_drawer_font_style) {
                $("html").attr("data-drawer-font-style", pl_drawer_details.pl_drawer_font_style);
            }

            if (pl_dynamic_css && pl_dynamic_css.pl_button_style) {
                ajax.loadCSS(`/pl_curved_backend_theme/static/src/scss/components/buttons/${pl_dynamic_css.pl_button_style}.css`);
            }
            if (pl_dynamic_css && pl_dynamic_css.pl_theme_style) {
                ajax.loadCSS(`/pl_curved_backend_theme/static/src/scss/components/theme_style/${pl_dynamic_css.pl_theme_style}.css`);
            }
            if (pl_dynamic_css && pl_dynamic_css.pl_tab_style) {
                ajax.loadCSS(`/pl_curved_backend_theme/static/src/scss/components/tab_style/${pl_dynamic_css.pl_tab_style}.css`);
            }

            if (pl_dynamic_css && pl_dynamic_css.pl_font_style) {
                ajax.loadCSS(`/pl_curved_backend_theme/static/src/scss/components/fonts/${pl_dynamic_css.pl_font_style}.css`);
            }

            if (pl_dynamic_css && pl_dynamic_css.pl_separator_style) {
                ajax.loadCSS(`/pl_curved_backend_theme/static/src/scss/components/separators/${pl_dynamic_css.pl_separator_style}.css`);
            }

            if (pl_dynamic_css && pl_dynamic_css.pl_checkbox_style) {
                ajax.loadCSS(`/pl_curved_backend_theme/static/src/scss/components/checkbox/${pl_dynamic_css.pl_checkbox_style}.css`);
            }

            if (pl_dynamic_css && pl_dynamic_css.pl_font_size) {
                ajax.loadCSS(`/pl_curved_backend_theme/static/src/scss/components/fontsize/${pl_dynamic_css.pl_font_size}.css`);
            }

            if (pl_dynamic_css && pl_dynamic_css.pl_chatter == "pl_chatter_right") {
                ajax.loadCSS(`/pl_curved_backend_theme/static/src/scss/components/chatter/${pl_dynamic_css.pl_chatter}.css`);
            }

            if (pl_dynamic_css && pl_dynamic_css.pl_radio_button_style) {
                ajax.loadCSS(`/pl_curved_backend_theme/static/src/scss/components/radiobutton/${pl_dynamic_css.pl_radio_button_style}.css`);
            }

            if (pl_dynamic_css && pl_dynamic_css.pl_popup_animation_style) {
                ajax.loadCSS(`/pl_curved_backend_theme/static/src/scss/components/popup_animation/${pl_dynamic_css.pl_popup_animation_style}.css`);
            }

            return _super(...arguments);
        },

        on_attach_callback: function() {
            $(".pl_image_hover").attr("data-zoom", 1);
            $(".pl_image_hover").zoomOdoo({
                event: "mouseenter",
                attach: ".pl_back_img_hover",
                zoom: true,
                attachToTarget: true,
                beforeAttach: function() {
                    this.$flyout.css({
                        width: "125px",
                        height: "125px"
                    });
                },
            });
            this._plManageCurrentColorTheme();
        },

        /**
       * @override
       **/
        start: function() {
            var res = this._super.apply(this, arguments);
            var self = this;

            // Remove unused css style
            if (this.pl_background && this.pl_background.pl_body_background && this.pl_background.pl_body_background.value) {}

            var pl_apply_dark_mode = true;

            // Check light and dark theme.
            if (!this.data.pl_dark_mode)
                pl_apply_dark_mode = false;

            if (this.data.pl_auto_dark_mode && this.data.pl_sun_time_info && this.data.pl_dark_mode) {
                // Check theme light/dark mode based on sun time.
                var pl_current_datetime = new Date();
                var pl_sunrise_datetime = new Date("01 Jan 2000 " + this.data.pl_sun_time_info.sunrise);
                var pl_sunset_datetime = new Date("01 Jan 2000 " + this.data.pl_sun_time_info.sunset);

                if (this._plCompareTime(pl_sunrise_datetime, pl_sunset_datetime, pl_current_datetime)) {
                    pl_apply_dark_mode = false;
                }
            }

            // Apply light/dark theme.
            if (pl_apply_dark_mode)
                $("html").attr("data-color-mode", "pl-dark");
            else
                $("html").attr("data-color-mode", "pl-light");
            session.pl_current_color_mode = $("html").attr("data-color-mode");
//            this._plManageCurrentColorTheme();
            return res;
        },

        _plManageCurrentColorTheme() {
            var pl_current_theme = session.pl_color_theme;
            var pl_header_icon_clr = this._plGetHeaderIconColor(pl_current_theme["body-background"]);

            // Change header icons color for light and when body color is dark.
            if (session.pl_current_color_mode == "pl-light" && pl_header_icon_clr == "white") {
                session.pl_color_theme.pl_header_icon_clr = pl_header_icon_clr;
                // Change header font icons to white.
                $("div.o_menu_systray").addClass("pl_color_theme_dark_header");
                $(".o_main_navbar button.phone-menu-btn").addClass("pl_color_theme_dark_header");
                $(".pl_left_sidebar_panel .pl_app_sidebar .inner-sidebar button.phone-menu-btn").addClass("pl_color_theme_dark_header");
            }

            // Control view bg color.
            if (session.pl_current_color_mode == "pl-light" && !pl_current_theme.default_theme) {
                document.body.style.setProperty("--pl-main-control-bg", "#FFFFFF");
                if (pl_header_icon_clr == "white") {
                    document.body.style.setProperty("--app-drawar", "#FFFFFF");
                }
            }

            if (pl_current_theme.primary) {
                document.body.style.setProperty("--primary", pl_current_theme.primary);
                if (pl_current_theme["body-background"] == pl_current_theme.primary && session.pl_current_color_mode == "pl-light") {
                    document.body.style.setProperty("--nav-primary", "#ffffff");
                } else {
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
            }
        },

        _plColorThemeResetToDefault: function() {
            this.pl_unsaved_setting = {};
            var default_color_theme = this.data.pl_color_theme.filter(x=>x.pl_default);
            if (default_color_theme.length) {
                this.pl_unsaved_setting['pl_theme_color'] = default_color_theme[0]['id'];
                this._plSettingSave();
            }
        },

        _onInputChange: function(ev) {
            var self = this;
            if (ev.target.name) {
                if (ev.target.type == "checkbox") {
                    var _value = ev.target.checked;
                    var _field = ev.target.name;
                } else if (ev.target.type == "radio") {
                    if (ev.target.attributes["data-value"]) {
                        var _value = ev.target.attributes["data-value"].value;
                        var _field = ev.target.name;
                    }
                }

                if (_field) {
                    this.pl_unsaved_setting[_field] = _value;
                    self.pl_dirty_data[_field] = $(ev.currentTarget);
                }

                // Handle binary field fields.
                if ($(ev.currentTarget).hasClass("pl_binary_field")) {
                    var file_node = ev.target;
                    // Handle body background input change.
                    // Active selected background image.
                    if (file_node.getAttribute("data-model")) {
                        var pl_img_src = $(file_node.nextElementSibling).find("img").attr("src");
                        var pl_value = self._plDecodeURLToString(pl_img_src);
                        if (file_node.id.split("#")[1] && parseInt(file_node.id.split("#")[1])) {
                            pl_value = parseInt(file_node.id.split("#")[1]);
                        }
                        this.pl_unsaved_setting[file_node.name] = false;
                        this.pl_unsaved_setting[file_node.getAttribute("data-field-save")] = pl_value;
                        self.pl_dirty_data[file_node.name] = $(ev.currentTarget);
                        self.pl_dirty_data[file_node.getAttribute("data-field-save")] = $(ev.currentTarget);
                    } else {
                        // Add new background image.
                        var file = file_node.files[0];
                        var field_name = ev.target.name;
                        //                        var pl_target = ev.currentTarget;
                        utils.getDataURLFromFile(file).then(function(data) {
                            data = data.split(",")[1];
                            // Create url for file
                            var url = "data:image/" + (self.file_type_magic_word[data[0]] || "png") + ";base64," + data;
                            $("." + field_name + "_preview").prop("src", url);
                            // self.pl_unsaved_setting[field_name] = data;
                            ajax.jsonRpc("/pl_curved_backend_theme/add/images", "call", {
                                image_info: {
                                    key: field_name,
                                    value: data
                                },
                                scope: "user",
                            }).then(function(res) {
                                var pl_template_data = {};
                                self._PlGetImageDict(field_name, pl_template_data);
                                pl_template_data["pl_image_data"] = res;

                                var pl_image_container = qweb.render("pl_theme_image_template", pl_template_data);

                                if (field_name == 'pl_body_background_img') {
                                    $('div.pl_body_background_img_container').html(pl_image_container);
                                }
                                if (field_name == 'pl_app_drawer_background_img') {
                                    $('div.pl_app_drawer_background_img_container').html(pl_image_container);
                                }

                                // Reattach odoo-zoom functionality.
                                self.on_attach_callback();
                            });
                        });
                    }
                }
                if ($(ev.currentTarget).attr("class").includes("slider")) {
                    $(ev.currentTarget).siblings(".pl_opacity_value_max").html(ev.currentTarget.value);
                    this.pl_unsaved_setting[ev.currentTarget.name] = ev.currentTarget.value;
                    self.pl_dirty_data[ev.currentTarget.name] = $(ev.currentTarget);
                }
                if(ev.currentTarget.value<=0.3){
                    document.getElementById("pl_drawer-quick-slider").classList.remove("d-none");
                  }
                  else{
                    document.getElementById("pl_drawer-quick-slider").classList.add("d-none");
                  }
                // Hide/show auto dark mode
                if (_field == "pl_dark_mode") {
                    this._plManageAutoDarkMode(_value);
                }

                if (_field == "pl_auto_dark_mode" && _value && !session.pl_curved_backend_theme_data.pl_sun_time_info) {
                    $("input#pl_auto_dark_mode").prop("checked", false);
                    this.pl_unsaved_setting.pl_auto_dark_mode = false;
                    self.pl_dirty_data['pl_auto_dark_mode'] = $(ev.currentTarget);
//                    this.do_warn(_t("Error"), _t("Please add sunrise and sunset time from user's preferences."));
                    this.displayNotification({
                        title: _t("Error"),
                        message: _t("Please add sunrise and sunset time from user's preferences.")
                    });
                }
            }
        },

        _PlGetImageDict: function(field_name, pl_template_data) {
            if (field_name == "pl_body_background_img") {
                pl_template_data["pl_image_for"] = "pl_body_background";
                pl_template_data["pl_image_save"] = "pl_body_background_img";
                pl_template_data["pl_image_del"] = "pl_body_background_del";
                pl_template_data["pl_image_add"] = "pl_body_background_img_user";
            }

            if (field_name == "pl_app_drawer_background_img") {
                pl_template_data["pl_image_for"] = "pl_app_drawer_background";
                pl_template_data["pl_image_save"] = "pl_app_drawer_background_img";
                pl_template_data["pl_image_del"] = "pl_drawer_background_del";
                pl_template_data["pl_image_add"] = "pl_app_drawer_background_user";
            }
        },

        _plApplyTempColorTheme: function(field_name, field_val) {
            var pl_color_field_dict = {
                pl_body_background_user: "--body-background",
                pl_menu_user: "--nav-link-color",
                pl_menu_hover_user: "--pl-over-link",
                pl_button_user: "--primary-btn",
                pl_border_user: "--tab-bg",
                pl_heading_user: "--heading-color",
                pl_link_user: "--link-color",
                pl_primary_color_user: "--primary",
                pl_tooltip_user: "--tooltip-heading-bg",
            };

            if (document.body.style.getPropertyValue(pl_color_field_dict[field_name])) {
                document.body.style.setProperty(pl_color_field_dict[field_name], field_val);
            }
        },

        _plDecodeURLToString: function(URL) {
            return URL.split(",")[1];
        },

        _plUserSettings: function(ev) {
            this.pl_unsaved_setting = {};
            document.body.classList.add("pl_stop_auto_hide");
        },

        _plHideUserSettings: function(ev) {
            document.body.classList.remove("pl_stop_auto_hide");
            this._plResetValues();
            this.pl_unsaved_setting = {};
            this._plUserThemeCancel();
        },

        _plGlobalSettings: function(ev) {
            var self = this;
            $(".pl-dropdown-close").click();
            if (!self.data["pl_global_config_id"])
                alert("Curved Theme Configuration Files Corrupted.");
            var dict = {
                name: _t("Lead or Opportunity"),
                res_model: "pl.global.config",
                res_id: self.data["pl_global_config_id"],
                views: [[false, "form"]],
                type: "ir.actions.act_window",
                context: {
                    form_view_ref: "pl_curved_backend_theme.pl_global_configuration_form",
                },

            };
            if($(document).find(".pl_appsmenu_active").length){
                $(".o_web_client").removeClass("pl_appsmenu_active");
            }
            return self.do_action(dict);
        },

        _plResetValues: function() {
            var self = this;
            for (var index in this.pl_unsaved_setting) {
                if (typeof session.pl_curved_backend_theme_data[index] == "boolean") {
                    if (index in self.pl_dirty_data) {
                        self.pl_dirty_data[index].prop("checked", session.pl_curved_backend_theme_data[index]);
                    } else {
                        $("input#" + index).prop("checked", session.pl_curved_backend_theme_data[index]);
                    }
                    if (index == "pl_dark_mode") {
                        if (session.pl_curved_backend_theme_data[index])
                            $("div#pl_auto_dark_mode_div").css("display", "block");
                        else
                            $("div#pl_auto_dark_mode_div").css("display", "none");
                    }
                    delete this.pl_unsaved_setting[index];
                } else if (!["pl_app_drawer_background", "pl_body_background", "pl_body_background_img", "pl_app_drawer_background_img", ].includes(index)) {
                        $("input#" + session.pl_curved_backend_theme_data[index]).prop("checked", true);
                    delete this.pl_unsaved_setting[index];
                }// clear input type file for body background and app drawer background.
                else if (["pl_body_background_img", "pl_app_drawer_background_img"].includes(index)) {
                    $(`p.${index}_user`).addClass("d-none");
                    delete this.pl_unsaved_setting[index];
                }
            }
            // function called to revert view changes on app drawer body background and color theme
            self._PlResetDirtyData(session)
            // Hide/Show Auto-dark mode
            if ("pl_dark_mode"in this.pl_unsaved_setting) {
                this._plManageAutoDarkMode(session.pl_curved_backend_theme_data.pl_dark_mode);
            }
            // Hide/Show Auto-dark mode
            if ("pl_dark_mode"in this.pl_unsaved_setting) {
                this._plManageAutoDarkMode(session.pl_curved_backend_theme_data.pl_dark_mode);
            }
        },

        _PlResetDirtyData: function(session) {
            var self = this;
            for (var index in self.pl_dirty_data) {
                if (index && self.pl_dirty_data[index] && (index in self.pl_dirty_data) && self.pl_dirty_data[index].attr('type') == 'range') {
                    //Handled toggle button case
                    self.pl_dirty_data[index].val(session.pl_curved_backend_theme_data[index])
                } else if (index && self.pl_dirty_data[index] && (index in self.pl_dirty_data) && self.pl_dirty_data[index].data('field-save') && self.pl_dirty_data[index].hasClass('pl_radio_list')) {
                    //Handled color theme and body background case
                    var active_rec = session.pl_curved_backend_theme_data[self.pl_dirty_data[index].data('field-save')].filter(x=>x.pl_active)
                    if (active_rec && active_rec.length) {
                        $('input[name=' + self.pl_dirty_data[index].attr('name') + '][data-value="' + active_rec[0]['id'] + '"]').prop('checked', true);
                    } else {
                        $.each($('input[name=' + self.pl_dirty_data[index].attr('name') + ']'), function(e) {
                            $(this).prop('checked', false);
                        });
                    }
                } else if (index && self.pl_dirty_data[index] && (index in self.pl_dirty_data) && self.pl_dirty_data[index].attr('name') == 'pl_app_drawer_background') {
                    //Handled app drawer case
                    var val = session.pl_curved_backend_theme_data[self.pl_dirty_data[index].attr('name')]
                    var ele_ = $('input[name=' + self.pl_dirty_data[index].attr('name') + '][data-value="' + val + '"]');
                    if (ele_ && ele_.length) {
                        ele_.prop('checked', true);
                    } else {
                        $.each($('input[name=' + self.pl_dirty_data[index].attr('name') + ']'), function(e) {
                            $(this).prop('checked', false);
                        });
                    }
                }else if (index && self.pl_dirty_data[index] && (index in self.pl_dirty_data) && self.pl_dirty_data[index].data('field-save') && self.pl_dirty_data[index].hasClass('pl_cancel_radio')) {
                    $('input[name=' + self.pl_dirty_data[index].attr('name') + '][data-value="' + session.pl_curved_backend_theme_data[self.pl_dirty_data[index].data('field-save')] + '"]').prop('checked', true);
                }
            }
            self.pl_dirty_data = {}
        },

        _plSettingSave: function() {
            var self = this;
            if (Object.keys(this.pl_unsaved_setting).length) {
                ajax.jsonRpc("/save/theme/settings", "call", {
                    pl_unsaved_setting: self.pl_unsaved_setting,
                    pl_origin_scope: "user",
                }).then(function() {
                    self.do_action("reload_context");
                });
            }
        },

        _plSettingCancel: function() {
            this._plResetValues();
            this._plUserThemeCancel();
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

        /*
       * Manage auto dark mode.
       */
        _plManageAutoDarkMode: function(value) {
            if (value) {
                // Show auto dark mode.
                this.$("div#pl_auto_dark_mode_div").css("display", "block");
            } else {
                // Hide.
                this.$("div#pl_auto_dark_mode_div").css("display", "none");
            }
        },

        _plDelBackgroundImage: function(ev) {
            var self = this;
            var pl_image_id = ev.currentTarget.getAttribute("data-id");
            pl_image_id = pl_image_id.split("#")[1];
            if (ev.target.classList.contains("pl_drawer_background_del")) {
                var pl_model = "pl.drawer.background";
            } else {
                var pl_model = "pl.body.background";
            }
            if (pl_image_id) {
                Dialog.confirm(this, _t("Are you sure you want to delete this record ?"), {
                    confirm_callback: function() {
                        return this._rpc({
                            model: pl_model,
                            method: "unlink",
                            args: [pl_image_id],
                        }).then(function() {
                            $(ev.currentTarget.parentElement.parentElement).remove();
                            // self.do_action("reload_context");
                        });
                    },
                });
            }
        },

        _plBackgroundDefault: function(ev) {
            var self = this;
            this._rpc({
                route: "/pltheme/background/default",
                params: {
                    pl_setting_scope: "User",
                    pl_default_info: {
                        field: "pl_body_background",
                        model: "pl.body.background",
                    },
                },
            }).then(function() {
                self.do_action("reload_context");
            });
        },

        _plDrawerBackgroundDefault: function(ev) {
            var self = this;
            this._rpc({
                route: "/pltheme/background/default",
                params: {
                    pl_setting_scope: "User",
                    pl_default_info: {
                        field: "pl_app_drawer_background",
                        model: "pl.drawer.background",
                    },
                },
            }).then(function() {
                self.do_action("reload_context");
            });
        },

        // Todo: needs to remove this function
        _plUserCustomThemeAdd: function(ev) {
            var self = this;
            var pl_edit_section = qweb.render("pl_theme_edit_section", {
                pl_theme_data: {},
            });
            $("div#user_theme_edit_section").html(pl_edit_section);
            self._scrollToDown();
        },

        // Todo: needs to remove this function
        _plUserThemeEdit: function(ev) {
            var self = this;
            var pl_theme_id = parseInt($(ev.currentTarget).attr("data-theme-id"));
            this._rpc({
                model: "pl.color.theme",
                method: "search_read",
                kwargs: {
                    domain: [["id", "=", pl_theme_id]],
                    fields: [],
                },
            }).then(function(arg) {
                if (arg[0].pl_template_id.length) {
                    arg[0].id = false;
                }
                var pl_edit_section = qweb.render("pl_theme_edit_section", {
                    pl_theme_data: arg[0],
                });
                $("div#user_theme_edit_section").html(pl_edit_section);
                self._scrollToDown();
            });
        },

        // Todo: needs to remove this function
        _plUserThemeCancel: function() {
            // Remove the theme edit section.
            $("div#user_theme_edit_section").html("");

            // Revert color theme temp changes.
            this._plResetColorTheme();
        },

        // Todo: needs to remove this function
        _plResetColorTheme() {
            var pl_color_field_dict = {
                pl_body_background_user: "body-background",
                pl_menu_user: "nav-link-color",
                pl_menu_hover_user: "pl-over-link",
                pl_button_user: "primary-btn",
                pl_border_user: "tab-bg",
                pl_heading_user: "heading-color",
                pl_link_user: "link-color",
                pl_primary_color_user: "primary",
                pl_tooltip_user: "tooltip-heading-bg",
            };
            _.each(pl_color_field_dict, (value,key)=>{
                if (document.body.style.getPropertyValue("--" + value)) {
                    document.body.style.setProperty("--" + value, session.pl_color_theme[value]);
                }
            }
            );
        },

        // Todo: needs to remove this function
        _pl_get_theme_data_dict: function() {
            var pl_data = {};
            this.pl_user_theme_fields.forEach((pl_element)=>{
                pl_data[pl_element] = $(`input#${pl_element}_user`).val();
            }
            );
            return pl_data;
        },

        // Todo: needs to remove this function
        _plUserThemeSave: function() {
            var self = this;
            var pl_theme_data = this._pl_get_theme_data_dict();
            pl_theme_data["pl_user"] = session.uid;
            this._rpc({
                model: "pl.color.theme",
                method: "create",
                args: [pl_theme_data],
            }).then(function(create_id) {
                self._rpc({
                    model: "pl.color.theme",
                    method: "search_read",
                    kwargs: {
                        domain: [["id", "=", create_id]],
                        fields: [],
                    },
                }).then(function(arg) {
                    self.data.pl_color_theme.custom.push(arg[0]);
                    var color_theme_temp = qweb.render("pl_color_theme_qweb_template", {
                        widget: self,
                    });
                    $("div.pl_color_theme_qweb_div_user").html(color_theme_temp);
                });
                // location.reload();
            });
        },

        // Todo: needs to remove this function
        _plUserThemeUpdate(ev) {
            var self = this;
            var pl_theme_data = this._pl_get_theme_data_dict();
            var pl_theme_id = parseInt($(ev.currentTarget).attr("data-theme-id"));
            this._rpc({
                model: "pl.color.theme",
                method: "write",
                args: [[pl_theme_id], pl_theme_data],
            }).then(function(arg) {
                self._rpc({
                    model: "pl.color.theme",
                    method: "search_read",
                    kwargs: {
                        domain: [["id", "=", pl_theme_id]],
                        fields: [],
                    },
                }).then(function(arg) {
                    self._updateThemeData(arg[0]);
                    // self.data.pl_color_theme.custom.push(arg[0]);
                    var color_theme_temp = qweb.render("pl_color_theme_qweb_template", {
                        widget: self,
                    });
                    $("div.pl_color_theme_qweb_div_user").html(color_theme_temp);
                });
                // location.reload();
                //                var pl_edit_section = qweb.render("pl_theme_edit_section", {pl_theme_data: arg[0]});
                //                $('div#user_theme_edit_section').html(pl_edit_section);
            });
        },

        // Todo: needs to remove this function
        _plUserThemeDelete: function(ev) {
            var self = this;
            var pl_theme_id = parseInt($(ev.currentTarget).attr("data-theme-id"));
            if (pl_theme_id) {
                Dialog.confirm(this, _t("Are you sure you want to delete this record ?"), {
                    confirm_callback: function() {
                        return this._rpc({
                            model: "pl.color.theme",
                            method: "unlink",
                            args: [pl_theme_id],
                        }).then(function() {
                            self._plRemoveTheme(pl_theme_id);
                            var color_theme_temp = qweb.render("pl_color_theme_qweb_template", {
                                widget: self,
                            });
                            $("div.pl_color_theme_qweb_div_user").html(color_theme_temp);
                            // self.do_action("reload_context");
                        });
                    },
                });
            }
        },

        // Todo: needs to remove this function
        _plRemoveTheme: function(pl_theme_id) {
            var result = false;
            var pl_custom_themes = _.filter(this.data.pl_color_theme.custom, function(theme) {
                return pl_theme_id != theme.id;
            });
            this.data.pl_color_theme.custom = pl_custom_themes;
            return result;
        },

        // Todo: needs to remove this function
        _scrollToDown: function() {
            // Scroll down div
            $("div.pl_color_theme_qweb_div_user").scrollTop($("div.pl_color_theme_qweb_div_user")[0].scrollHeight);
        },

        // Todo: needs to remove this function
        _updateThemeData: function(updated_data) {
            var pl_updated_data = _.map(this.data.pl_color_theme.custom, function(theme) {
                if (theme.id == updated_data.id)
                    return updated_data;
                else
                    return theme;
            });
            this.data.pl_color_theme.custom = pl_updated_data;
        },

        _plHexToRGB: function(hex) {
            var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            return result ? {
                r: parseInt(result[1], 16),
                g: parseInt(result[2], 16),
                b: parseInt(result[3], 16),
            } : null;
        },

        _plGetHeaderIconColor: function(pl_color) {
            var rgb = [];
            var pl_up_color = this._plHexToRGB(pl_color);
            rgb[0] = pl_up_color.r;
            rgb[1] = pl_up_color.g;
            rgb[2] = pl_up_color.b;

            const pl_brightness = Math.round((parseInt(rgb[0]) * 299 + parseInt(rgb[1]) * 587 + parseInt(rgb[2]) * 114) / 1000);
            const pl_result = pl_brightness > 125 ? "black" : "white";

            return pl_result;
        },
    });
    SystrayMenu.Items.push(PlQuickSettings);
    return PlQuickSettings;
});
