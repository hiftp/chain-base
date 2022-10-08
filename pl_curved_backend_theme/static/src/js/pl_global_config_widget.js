odoo.define("pl_curved_backend_theme.pl_global_config_widget", function(require) {
    "use strict";

    var core = require("web.core");
    var Widget = require("web.Widget");
    var widgetRegistry = require("web.widget_registry");
    var ajax = require("web.ajax");
    var utils = require("web.utils");
    var Dialog = require("web.Dialog");
    var session = require("web.session");
    var QWeb = core.qweb;
    var _t = core._t;

    var QWeb = core.qweb;

    var PlGlobalConfigWidget = Widget.extend({
        template: "pl_global_settings",

        file_type_magic_word: {
            "/": "jpg",
            R: "gif",
            i: "png",
            P: "svg+xml",
        },

        events: _.extend({}, Widget.prototype.events, {
            "click .pl_global_apply_scope": "_plApplyScope",
            "change input": "_onInputChange",
            "click .pl_save_global_data": "_plSaveGlobalData",
            "click .pl_body_background_del_global, .pl_drawer_background_global_del": "_plDelBackgroundImage",
            "click .pl_login_background_image_del": "_plDelLoginBackgroundImage",
            "click .pl_login_background_color_del": "_plDelLoginBackgroundColor",
            "click .pl_background_default_global": "_plBackgroundDefault",
            "click .pl_drawer_background_default_global": "_plDrawerDefault",
            "click button.pl_setting_cancel_global": "_plSettingCancel",
            "click .pl_global_theme_edit": "_plColorThemeEdit",
            "click button#pl_add_custom_theme_global": "_plCustomColorThemeAdd",
            "click .pl_theme_edit_cancel": "_plColorThemeCancel",
            "click .pl_new_theme_save": "_plColorThemeSave",
            "click .pl_theme_edit_update": "_plColorThemeUpdate",
            "click .pl_global_theme_delete": "_plColorThemeDelete",
            "click .pl_global_reset_color_theme": "_plColorThemeResetToDefault",
            "click .pl_add_login_color": "_plLoginPageBgColor",
        }),
        // Todo: Take reference from Ribbon widget
        init: function(parent, data, options) {
            this.pl_unsaved_data = {};
            this.pl_unsaved_theme_global_data = {};
            this.pl_dirty_data = {}
            this.pl_global_theme_fields = ["pl_body_background", "pl_menu", "pl_menu_hover", "pl_button", "pl_border", "pl_heading", "pl_link", "pl_primary_color", "pl_tooltip", "name", ];
            this._super.apply(this, arguments);
        },

        /**
       * @override
       **/
        willStart: async function() {
            const _super = this._super.bind(this);
            const data = await this._rpc({
                args: [],
                method: "pl_get_config_values",
                model: "pl.global.config",
            });
            const pl_theme_global_data = await this._rpc({
                route: "/render/theme/view/data",
                params: {
                    pl_setting_scope: "Global"
                },
            });
            if (data) {
                this.data = data;
            }
            if (pl_theme_global_data) {
                this.pl_color_theme_scope = pl_theme_global_data.pl_color_theme_scope == "Global" ? true : false;
                this.pl_theme_global_data = pl_theme_global_data;
            }
            return _super(...arguments);
        },

        on_attach_callback: function() {
            this._plAttachImageZoom();
        },

        _plAttachImageZoom(){
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
        },

        _plColorThemeResetToDefault: function() {
            this.pl_unsaved_data = {}
            var default_color_theme = this.pl_theme_global_data.pl_color_theme.predefined.filter(x=>x.pl_default)
            if (default_color_theme.length) {
                this.pl_unsaved_theme_global_data['pl_theme_color'] = default_color_theme[0]['id'];
                this._plSaveGlobalData();
            }
        },

        _render: function() {
            this._super.apply(this, arguments);
            var pl_self = this;
        },

        _plApplyScope: function() {
            var self = this;
            if (this.pl_unsaved_data) {
                this._rpc({
                    args: [this.pl_unsaved_data],
                    method: "pl_save_apply_scope",
                    model: "pl.global.config",
                }).then(function() {
                    self.do_action("reload_context");
                });
            }
        },

        _onInputChange: function(ev) {
            var self = this;
            if (!$(ev.currentTarget).parents('#global_theme_edit_section').length) {
                if (ev.currentTarget.name && ev.currentTarget.dataset.value != this.data[ev.currentTarget.name] && ev.currentTarget.hasAttribute("pl_curve_scope_input")) {
                    this.pl_unsaved_data[ev.currentTarget.name] = ev.currentTarget.dataset.value;
                    self.pl_dirty_data[ev.currentTarget.name] = $(ev.currentTarget);
                } else if (ev.currentTarget.name) {
                    delete this.pl_unsaved_data[ev.currentTarget.name];
                }

                // Condition to change global setting fields and boolean fields.
                if (ev.currentTarget.name.split("scope").length < 2 && !$(ev.currentTarget).hasClass("pl_binary_field")) {
                    this.pl_unsaved_theme_global_data[ev.currentTarget.name] = ev.currentTarget.dataset.value ? ev.currentTarget.dataset.value : ev.currentTarget.checked;
                    self.pl_dirty_data[ev.currentTarget.name] = $(ev.currentTarget);
                }
                if ($(ev.currentTarget).attr("class") && $(ev.currentTarget).attr("class").includes("slider")) {
                    $(ev.currentTarget).siblings(".pl_opacity_value_max").html(ev.currentTarget.value);
                    this.pl_unsaved_theme_global_data[ev.currentTarget.name] = ev.currentTarget.value;
                    self.pl_dirty_data[ev.currentTarget.name] = $(ev.currentTarget);
                }
                if(ev.currentTarget.value<=0.3){
                    document.getElementById("pl-drawer-global-slider").classList.remove("d-none");
                  }
                  else{
                    if(document.getElementById("pl-drawer-global-slider")){
                        document.getElementById("pl-drawer-global-slider").classList.add("d-none");
                    }
                  }
                // Manage data for text fields.
                if (ev.currentTarget.name && ev.currentTarget.dataset.type == "pl-char") {
                    this.pl_unsaved_theme_global_data[ev.currentTarget.name] = ev.currentTarget.value;
                    self.pl_dirty_data[ev.currentTarget.name] = $(ev.currentTarget);
                }

                // Handle binary field fields.
                // Set background image active true.
                if ($(ev.currentTarget).hasClass("pl_binary_field")) {
                    var file_node = ev.target;
                    // Handle body background input change.
                    if (file_node.getAttribute("data-model")) {
                        var pl_img_src = $(file_node.nextElementSibling).find("img").attr("src");
                        var pl_value = self._plDecodeURLToString(pl_img_src);
                        if (file_node.id.split("#")[1] && parseInt(file_node.id.split("#")[1])) {
                            pl_value = parseInt(file_node.id.split("#")[1]);
                        }
                        this.pl_unsaved_theme_global_data[file_node.name] = false;
                        this.pl_unsaved_theme_global_data[file_node.getAttribute("data-field-save")] = pl_value;
                        self.pl_dirty_data[file_node.name] = $(ev.currentTarget);
                        self.pl_dirty_data[file_node.getAttribute("data-field-save")] = $(ev.currentTarget);
                    } else {
                        // create background image data.
                        var file = file_node.files[0];
                        var field_name = ev.target.name;
                        utils.getDataURLFromFile(file).then(function(data) {
                            data = data.split(",")[1];
                            // Create url for file
                            var url = "data:image/" + (self.file_type_magic_word[data[0]] || "png") + ";base64," + data;
                            $("." + field_name + "_preview").prop("src", url);
                            // self.pl_unsaved_theme_global_data[field_name] = data;
                            if ($(ev.currentTarget).hasClass("pl_background_image")) {
                                ajax.jsonRpc("/pl_curved_backend_theme/add/images", "call", {
                                    image_info: {
                                        key: field_name,
                                        value: data
                                    },
                                    scope: "global",
                                }).then(function(res) {
                                    var pl_template_data = {};
                                    self._PlGetImageDict(field_name, pl_template_data);
                                    pl_template_data["pl_image_data"] = res;

                                    var pl_image_container = QWeb.render("pl_theme_image_template", pl_template_data);

                                    if (field_name == "pl_body_background_img") {
                                        $("div.pl_body_background_global_container").html(pl_image_container);
                                    }
                                    if (field_name == "pl_app_drawer_background_img") {
                                        $("div.pl_app_drawer_background_global_container").html(pl_image_container);
                                    }
                                    // function to reattach zoom functionality on image.
                                    self._plAttachImageZoom();
                                });
                            }

                            if($(ev.currentTarget).hasClass("pl_login_background_image")){
                                ajax.jsonRpc("/pl_curved_backend_theme/add/login/images", "call", {
                                    image_info: {
                                        key: field_name,
                                        value: data
                                    }
                                }).then(function(res) {
                                    var pl_template_data = {};
                                    self._PlGetImageDict(field_name, pl_template_data);
                                    pl_template_data["pl_login_image"] = res;

                                    var pl_image_container = QWeb.render("pl_login_background_image_template", pl_template_data);

                                    if (field_name == "pl_login_background_image") {
                                        $("div.pl_login_background_img_container").html(pl_image_container);
                                    }
                                    // function to reattach zoom functionality on image.
                                    self._plAttachImageZoom();
                                });
                            }
                            else {
                                $("." + field_name + "_preview").prop("src", url);
                                self.pl_unsaved_theme_global_data[field_name] = data;
                            }
                        });
                    }
                }
            } else {
                // Handle color theme input
                var pl_color_theme_fields = ["pl_body_background_global", "pl_menu_global", "pl_menu_hover_global", "pl_button_global", "pl_border_global", "pl_heading_global", "pl_link_global", "pl_primary_color_global", "pl_tooltip_global", ];

                if (pl_color_theme_fields.includes(ev.currentTarget.name)) {
                    this._plApplyTempColorTheme(ev.currentTarget.name, ev.currentTarget.value);
                }
            }
        },

        _PlGetImageDict: function(field_name, pl_template_data) {
            if (field_name == "pl_body_background_img") {
                pl_template_data["pl_image_for"] = "pl_body_background_global";
                pl_template_data["pl_image_save"] = "pl_body_background_img";
                pl_template_data["pl_image_del"] = "pl_body_background_del_global";
                pl_template_data["pl_image_add"] = "pl_body_background_img_global";
            }

            if (field_name == "pl_app_drawer_background_img") {
                pl_template_data["pl_image_for"] = "pl_app_drawer_background_global";
                pl_template_data["pl_image_save"] = "pl_app_drawer_background_img";
                pl_template_data["pl_image_del"] = "pl_drawer_background_global_del";
                pl_template_data["pl_image_add"] = "pl_app_drawer_background_global";
            }
        },

        _plApplyTempColorTheme: function(field_name, field_val) {
            var pl_color_field_dict = {
                pl_body_background_global: "--body-background",
                pl_menu_global: "--nav-link-color",
                pl_menu_hover_global: "--pl-over-link",
                pl_button_global: "--primary-btn",
                pl_border_global: "--tab-bg",
                pl_heading_global: "--heading-color",
                pl_link_global: "--link-color",
                pl_primary_color_global: "--primary",
                pl_tooltip_global: "--tooltip-heading-bg",
            };

            if (document.body.style.getPropertyValue(pl_color_field_dict[field_name])) {
                document.body.style.setProperty(pl_color_field_dict[field_name], field_val);
            }
        },

        _plDecodeURLToString: function(URL) {
            return URL.split(",")[1];
        },

        _plSaveGlobalData: function(ev) {
            var self = this;
            if (Object.keys(this.pl_unsaved_theme_global_data).length) {
                ajax.jsonRpc("/save/theme/settings", "call", {
                    pl_unsaved_setting: this.pl_unsaved_theme_global_data,
                    pl_origin_scope: "global",
                }).then(function() {
                    self.do_action("reload_context");
                });
            }
        },

        _plDelBackgroundImage: function(ev) {
            var self = this;
            var pl_image_id = ev.currentTarget.getAttribute("data-id");
            pl_image_id = pl_image_id.split("#")[1];
            if (ev.target.classList.contains("pl_drawer_background_global_del")) {
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

        _plDelLoginBackgroundImage: function(ev){
            var self = this;
            var pl_image_id = ev.currentTarget.getAttribute("data-id");
            pl_image_id = pl_image_id.split("#")[1];
            if (pl_image_id) {
                Dialog.confirm(this, _t("Are you sure you want to delete this record ?"), {
                    confirm_callback: function() {
                        return this._rpc({
                            model: "pl.login.background.image",
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

        _plDelLoginBackgroundColor: function(ev){
            var self = this;
            var pl_color_id = ev.currentTarget.getAttribute("data-id");
            pl_color_id = pl_color_id.split("#")[1];
            debugger;
            if (pl_color_id) {
                Dialog.confirm(this, _t("Are you sure you want to delete this record ?"), {
                    confirm_callback: function() {
                        return this._rpc({
                            model: "pl.login.background.color",
                            method: "unlink",
                            args: [pl_color_id],
                        }).then(function() {
                            $(ev.currentTarget.parentElement.parentElement).remove();
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
                    pl_setting_scope: "Global",
                    pl_default_info: {
                        field: "pl_body_background",
                        model: "pl.body.background",
                    },
                },
            }).then(function() {
                self.do_action("reload_context");
            });
        },

        _plDrawerDefault: function(ev) {
            var self = this;
            this._rpc({
                route: "/pltheme/background/default",
                params: {
                    pl_setting_scope: "Global",
                    pl_default_info: {
                        field: "pl_app_drawer_background",
                        model: "pl.drawer.background",
                    },
                },
            }).then(function() {
                self.do_action("reload_context");
            });
        },

        _plSettingCancel: function() {
            this._plResetValues();
            this._plColorThemeCancel();
        },

        _plResetValues: function() {
            var self = this;
            var pl_session = this.pl_theme_global_data;
            var pl_splitter = "_global";
            for (var index in this.pl_unsaved_theme_global_data) {
                let pl_index = index.split(pl_splitter)[0];
                // Ignore unsupported fields.
                if (!["pl_app_drawer_background_img", "pl_app_drawer_background_opacity", "pl_body_background_img", "pl_body_background_opacity", "pl_company_logo", "pl_login_background_image", "pl_small_company_logo", "pl_website_title", ].includes(pl_index)) {
                    if (typeof pl_session[pl_index] == "boolean") {
                        $(`input#${pl_index}${pl_splitter}`).prop("checked", pl_session[pl_index]);
                    } else if (!["pl_app_drawer_background", "pl_body_background"].includes(pl_index)) {
                        $(`input#${pl_session[pl_index]}${pl_splitter}`).prop("checked", true);
                    }
                } else if (["pl_body_background_img", "pl_app_drawer_background_img"].includes(index)) {
                    $(`p.${index}_global`).addClass("d-none");
                }
                delete this.pl_unsaved_theme_global_data[index];
            }
            // Reset background image and color for background and app drawer.
            ["pl_body_background_global", "pl_app_drawer_background_global", ].forEach((element)=>{
                $(`input[name=${element}]:checked`).prop("checked", false);
                $(`input[name=${element}][checked=checked]`).prop("checked", true);
            }
            );
            // function called to revert view changes  body background and color theme
            self._PlResetDirtyData(pl_session, pl_splitter);
        },
        _PlResetDirtyData: function(pl_session, pl_splitter) {
            var self = this;
            for (var index in self.pl_dirty_data) {
                if (index && self.pl_dirty_data[index] && (index.split(pl_splitter)[0]in pl_session) && self.pl_dirty_data[index].attr('type') == 'range') {
                    //Handled toggle button case
                    self.pl_dirty_data[index].val(pl_session[index.split(pl_splitter)[0]])
                } else if (index && self.pl_dirty_data[index] && (self.pl_dirty_data[index].data('field-save')in pl_session) && self.pl_dirty_data[index].data('field-save') && self.pl_dirty_data[index].hasClass('pl_radio_list')) {
                    //Handled color theme and body background case
                    var active_rec = [];
                    if (Array.isArray(pl_session[self.pl_dirty_data[index].data('field-save')])) {
                        var active_rec = pl_session[self.pl_dirty_data[index].data('field-save')].filter(x=>x.pl_active)
                    } else {
                        for (var key in pl_session[self.pl_dirty_data[index].data('field-save')]) {
                            active_rec = pl_session[self.pl_dirty_data[index].data('field-save')][key].filter(x=>x.pl_active);
                            if (active_rec && active_rec.length)
                                break;
                        }
                    }
                    if (active_rec && active_rec.length) {
                        $('input[name=' + self.pl_dirty_data[index].attr('name') + '][data-value="' + active_rec[0]['id'] + '"]').prop('checked', true);
                    } else {
                        $.each($('input[name=' + self.pl_dirty_data[index].attr('name') + ']'), function(e) {
                            $(this).prop('checked', false);
                        });
                    }
                }else if (index && self.pl_dirty_data[index] && (self.pl_dirty_data[index].data('field-save')in pl_session) && self.pl_dirty_data[index].data('field-save') && self.pl_dirty_data[index].hasClass('pl_cancel_radio')) {
                    $('input[name=' + self.pl_dirty_data[index].attr('name') + '][data-value="' + pl_session[self.pl_dirty_data[index].data('field-save')] + '"]').prop('checked', true);
                }
            }
            self.pl_dirty_data = {}

        },

        _plColorThemeEdit: function(ev) {
            var self = this;
            var pl_theme_id = parseInt($(ev.currentTarget).attr("data-theme-id"));
            $("div.pl_theme_selected").removeClass("pl_theme_selected");
            $(ev.currentTarget.parentElement.parentElement).addClass("pl_theme_selected");
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
                var pl_edit_section = QWeb.render("pl_theme_edit_section_global", {
                    pl_theme_data: arg[0],
                });
                $("div#global_theme_edit_section").html(pl_edit_section);
                self._scrollToDown();
            });
        },

        _scrollToDown: function() {
            // Scroll down div
            $("div.pl_color_theme_qweb_div_global").scrollTop($("div.pl_color_theme_qweb_div_global")[0].scrollHeight);
        },

        _plCustomColorThemeAdd: function() {
            var self = this;
            var pl_edit_section = QWeb.render("pl_theme_edit_section_global", {
                pl_theme_data: {},
            });
            $("div#global_theme_edit_section").html(pl_edit_section);
            self._scrollToDown();
        },

        _plColorThemeCancel: function() {
            $("div#global_theme_edit_section").html("");
            $("div.pl_theme_selected").removeClass("pl_theme_selected");
            this._plResetColorTheme();
        },

        _plResetColorTheme() {
            var pl_color_field_dict = {
                pl_body_background: "body-background",
                pl_menu: "nav-link-color",
                pl_menu_hover: "pl-over-link",
                pl_button: "primary-btn",
                pl_border: "tab-bg",
                pl_heading: "heading-color",
                pl_link: "link-color",
                pl_primary_color: "primary",
                pl_tooltip: "tooltip-heading-bg",
            };
            _.each(pl_color_field_dict, (value,key)=>{
                if (document.body.style.getPropertyValue("--" + value)) {
                    document.body.style.setProperty("--" + value, session.pl_color_theme[value]);
                }
            }
            );
        },

        _plColorThemeSave: function() {
            var self = this;
            var pl_theme_data = this._pl_get_theme_data_dict();
            pl_theme_data["pl_global"] = true;
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
                    self.pl_theme_global_data.pl_color_theme.custom.push(arg[0]);
                    var color_theme_temp = QWeb.render("pl_color_theme_qweb_template_global", {
                        widget: self,
                    });
                    $("div.pl_color_theme_qweb_div_global").html(color_theme_temp);
                });
            });
        },

        _pl_get_theme_data_dict: function() {
            var pl_data = {};
            this.pl_global_theme_fields.forEach((pl_element)=>{
                pl_data[pl_element] = $(`input#${pl_element}_global`).val();
            }
            );
            return pl_data;
        },

        _plColorThemeUpdate: function(ev) {
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
                    var color_theme_temp = QWeb.render("pl_color_theme_qweb_template_global", {
                        widget: self,
                    });
                    $("div.pl_color_theme_qweb_div_global").html(color_theme_temp);
                });
            });
        },

        _updateThemeData: function(updated_data) {
            var pl_updated_data = _.map(this.pl_theme_global_data.pl_color_theme.custom, function(theme) {
                if (theme.id == updated_data.id)
                    return updated_data;
                else
                    return theme;
            });
            this.pl_theme_global_data.pl_color_theme.custom = pl_updated_data;
        },

        _plColorThemeDelete: function(ev) {
            var self = this;
            var pl_theme_id = parseInt($(ev.currentTarget).attr("data-theme-id"));
            $("div.pl_theme_selected").removeClass("pl_theme_selected");
            $(ev.currentTarget.parentElement.parentElement).addClass("pl_theme_selected");
            if (pl_theme_id) {
                Dialog.confirm(this, _t("Are you sure you want to delete this record ?"), {
                    confirm_callback: function() {
                        return this._rpc({
                            model: "pl.color.theme",
                            method: "unlink",
                            args: [pl_theme_id],
                        }).then(function() {
                            self._plRemoveTheme(pl_theme_id);
                            var color_theme_temp = QWeb.render("pl_color_theme_qweb_template_global", {
                                widget: self,
                            });
                            $("div.pl_color_theme_qweb_div_global").html(color_theme_temp);
                        });
                    },
                    cancel_callback: ()=>{
                        $("div.pl_theme_selected").removeClass("pl_theme_selected");
                    }
                    ,
                });
            }
        },

        _plRemoveTheme: function(pl_theme_id) {
            var result = false;
            var pl_custom_themes = _.filter(this.pl_theme_global_data.pl_color_theme.custom, function(theme) {
                return pl_theme_id != theme.id;
            });
            this.pl_theme_global_data.pl_color_theme.custom = pl_custom_themes;
            return result;
        },

        on_detach_callback: function() {
            this._plColorThemeCancel();
        },

        _plLoginPageBgColor: function(){
            var pl_selected_color = $('#pl_login_bg_color_add').val();
            ajax.jsonRpc("/pl_curved_backend_theme/add/login/color", "call", {
                data: {
                   value: pl_selected_color
                },
            }).then(function(res) {
                var pl_template_data = {};
                pl_template_data["pl_login_colors"] = res;
                var pl_color_container = QWeb.render("pl_login_background_color_template", pl_template_data);
                $("div.pl_login_background_color_container").html(pl_color_container);
            });
        },
    });

    widgetRegistry.add("pl_global_config_widget", PlGlobalConfigWidget);

    return PlGlobalConfigWidget;
});
