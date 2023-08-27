odoo.define("pl_curved_backend_theme.pl_company_config_widget", function(require) {
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

    var PlCompanyConfigWidget = Widget.extend({
        template: "pl_company_settings",

        file_type_magic_word: {
            "/": "jpg",
            R: "gif",
            i: "png",
            P: "svg+xml",
        },

        events: {
            "change input": "_onInputChange",
            "click button.pl_setting_company_save": "_plSettingSave",
            "click .pl_body_background_del_company, .pl_drawer_background_company_del": "_plDelBackgroundImage",
            "click .pl_background_default_company": "_plBackgroundDefault",
            "click .pl_drawer_background_default_company": "_plDrawerDefault",
            "click button.pl_setting_cancel_company": "_plSettingCancel",
            "click .pl_company_theme_edit": "_plColorThemeEdit",
            "click button#pl_add_custom_theme_company": "_plCustomColorThemeAdd",
            "click .pl_theme_edit_cancel": "_plColorThemeCancel",
            "click .pl_new_theme_save": "_plColorThemeSave",
            "click .pl_theme_edit_update": "_plColorThemeUpdate",
            "click .pl_company_theme_delete": "_plColorThemeDelete",
            "click .pl_company_reset_color_theme": "_plColorThemeResetToDefault",
        },
        // Todo: Take reference from Ribbon widget
        init: function(parent, data, options) {
            this.pl_form_id = parent.state.data.id;
            this.pl_unsaved_setting = {};
            this.pl_dirty_data = {};
            this.pl_company_theme_fields = ["pl_body_background", "pl_menu", "pl_menu_hover", "pl_button", "pl_border", "pl_heading", "pl_link", "pl_primary_color", "pl_tooltip", ];
            this._super.apply(this, arguments);
        },

        /**
       * @override
       **/
        willStart: async function() {
            const _super = this._super.bind(this);
            const data = await this._rpc({
                route: "/render/theme/view/data",
                params: {
                    pl_setting_scope: "Company",
                    pl_rec_id: this.pl_form_id
                },
            });
            this.data = data;
            return _super(...arguments);
        },

        /**
       * @override
       */
        start: function() {
            var pl_self = this;
            return this._super.apply(this, arguments);
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
        },

        _plColorThemeResetToDefault: function() {
            this.pl_unsaved_setting = {};
            var default_color_theme = this.data.pl_color_theme.filter(x=>x.pl_default);
            if (default_color_theme.length) {
                this.pl_unsaved_setting['pl_theme_color'] = default_color_theme[0]['id'];
                this._plSettingSave();
            }
        },

        _render: function() {
            this._super.apply(this, arguments);
            var pl_self = this;
        },

        _onInputChange: function(ev) {
            var self = this;
            if (ev.currentTarget.name && !$(ev.currentTarget).hasClass("pl_binary_field")) {
                if (ev.currentTarget.dataset.type == "field-boolean") {
                    this.pl_unsaved_setting[ev.currentTarget.name] = ev.currentTarget.checked;
                    self.pl_dirty_data[ev.currentTarget.name] = $(ev.currentTarget);
                } else {
                    if ($(ev.currentTarget).attr("class").includes("slider")) {
                        $(ev.currentTarget).siblings(".pl_opacity_value_max").html(ev.currentTarget.value);
                        this.pl_unsaved_setting[ev.currentTarget.name] = ev.currentTarget.value;
                        self.pl_dirty_data[ev.currentTarget.name] = $(ev.currentTarget);
                    } else {
                        this.pl_unsaved_setting[ev.currentTarget.name] = ev.currentTarget.dataset.value ? ev.currentTarget.dataset.value : ev.currentTarget.checked;
                        self.pl_dirty_data[ev.currentTarget.name] = $(ev.currentTarget);
                    }
                if(ev.currentTarget.value<=0.3){
                    document.getElementById("pl-drawer-comp-slider").classList.remove("d-none");
                }
                else{
                    if(document.getElementById("pl-drawer-comp-slider")){
                    document.getElementById("pl-drawer-comp-slider").classList.add("d-none");
                }}
                }
            } else if (ev.currentTarget.name && !$(ev.currentTarget).hasClass("pl_binary_field")) {
                delete this.pl_unsaved_setting[ev.currentTarget.name];
            }

            // Manage data for text fields.
            if (ev.currentTarget.name && ev.currentTarget.dataset.type == "pl-char") {
                this.pl_unsaved_setting[ev.currentTarget.name] = ev.currentTarget.value;
                self.pl_dirty_data[ev.currentTarget.name] = $(ev.currentTarget);
            }

            // Handle binary field fields.
            if ($(ev.currentTarget).hasClass("pl_binary_field")) {
                var file_node = ev.target;
                // Handle body background input change.
                // set active saved image.
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
                    // add new image.
                    var file = file_node.files[0];
                    var field_name = ev.target.name;
                    utils.getDataURLFromFile(file).then(function(data) {
                        data = data.split(",")[1];
                        // Create url for file
                        var url = "data:image/" + (self.file_type_magic_word[data[0]] || "png") + ";base64," + data;
                        $("." + field_name + "_preview").prop("src", url);
                        // self.pl_unsaved_setting[field_name] = data;
                        if ($(ev.currentTarget).hasClass("pl_background_image")) {
                            ajax.jsonRpc("/pl_curved_backend_theme/add/images", "call", {
                                image_info: {
                                    key: field_name,
                                    value: data
                                },
                                scope: "company",
                                company_id: self.pl_form_id,
                            }).then(function(res) {
                                var pl_template_data = {};
                                self._PlGetImageDict(field_name, pl_template_data);
                                pl_template_data["pl_image_data"] = res;

                                var pl_image_container = QWeb.render("pl_theme_image_template", pl_template_data);

                                if (field_name == "pl_body_background_img") {
                                    $("div.pl_body_background_company_container").html(pl_image_container);
                                }
                                if (field_name == "pl_app_drawer_background_img") {
                                    $("div.pl_app_drawer_background_company_container").html(pl_image_container);
                                }
                                // function to reattach zoom functionality on image.
                                self.on_attach_callback();
                            });
                        } else{
                            $("." + field_name + "_preview").prop("src", url);
                            self.pl_unsaved_setting[field_name] = data;
                        }
                        // $(ev.currentTarget)
                        //   .parents(".pl-quick-card")
                        //   .find(".pl_bck_img")
                        //   .removeClass("d-none");
                    });
                }
            }
        },

        _PlGetImageDict: function(field_name, pl_template_data) {
            if (field_name == "pl_body_background_img") {
                pl_template_data["pl_image_for"] = "pl_body_background_company";
                pl_template_data["pl_image_save"] = "pl_body_background_img";
                pl_template_data["pl_image_del"] = "pl_body_background_del_company";
                pl_template_data["pl_image_add"] = "pl_body_background_company";
            }

            if (field_name == "pl_app_drawer_background_img") {
                pl_template_data["pl_image_for"] = "pl_app_drawer_background_company";
                pl_template_data["pl_image_save"] = "pl_app_drawer_background_img";
                pl_template_data["pl_image_del"] = "pl_drawer_background_company_del";
                pl_template_data["pl_image_add"] = "pl_app_drawer_background_company";
            }
        },

        _plApplyTempColorTheme: function(field_name, field_val) {
            var pl_color_field_dict = {
                pl_body_background_company: "--body-background",
                pl_menu_company: "--nav-link-color",
                pl_menu_hover_company: "--pl-over-link",
                pl_button_company: "--primary-btn",
                pl_border_company: "--tab-bg",
                pl_heading_company: "--heading-color",
                pl_link_company: "--link-color",
                pl_primary_color_company: "--primary",
                pl_tooltip_company: "--tooltip-heading-bg",
            };

            if (document.body.style.getPropertyValue(pl_color_field_dict[field_name])) {
                document.body.style.setProperty(pl_color_field_dict[field_name], field_val);
            }
        },

        _plDecodeURLToString: function(URL) {
            return URL.split(",")[1];
        },

        _plSettingSave: function(ev) {
            var self = this;
            if (Object.keys(this.pl_unsaved_setting).length) {
                ajax.jsonRpc("/save/theme/settings", "call", {
                    pl_unsaved_setting: self.pl_unsaved_setting,
                    pl_origin_scope: "company",
                    record_id: this.pl_form_id,
                }).then(function() {
                    self.do_action("reload_context");
                });
            }
        },

        _plDelBackgroundImage: function(ev) {
            var self = this;
            var pl_image_id = ev.currentTarget.getAttribute("data-id");
            pl_image_id = pl_image_id.split("#")[1];
            if (ev.target.classList.contains("pl_drawer_background_company_del")) {
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
                    pl_setting_scope: "Company",
                    pl_rec_id: this.pl_form_id,
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
                    pl_setting_scope: "Company",
                    pl_rec_id: this.pl_form_id,
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
            var self = this;
            var pl_session = this.data;
            var pl_splitter = "_company";
            for (var index in this.pl_unsaved_setting) {
                let pl_index = index.split(pl_splitter)[0];
                if (index == "pl_company_logo_enable_company") {
                    pl_index = "pl_company_logo_enable";
                }
                // Ignore unsupported fields.
                if (!["pl_app_drawer_background_img", "pl_app_drawer_background_opacity", "pl_body_background_img", "pl_body_background_opacity", "pl_company_logo", "pl_login_background_image", "pl_small_company_logo", "pl_website_title", "pl_app_drawer_background", "pl_body_background", "pl_company_logo", ].includes(pl_index)) {
                    if (typeof pl_session[pl_index] == "boolean") {
                        $(`input#${pl_index}${pl_splitter}`).prop("checked", pl_session[pl_index]);
                    } else {
                        $(`input#${pl_session[pl_index]}${pl_splitter}`).prop("checked", true);
                    }
                } else if (["pl_body_background_img", "pl_app_drawer_background_img"].includes(index)) {
                    $(`p.${index}_company`).addClass("d-none");
                }
                delete this.pl_unsaved_setting[index];
            }
            // Reset background image and color for background and app drawer.
            ["pl_body_background_company", "pl_app_drawer_background_company", ].forEach((element)=>{
                $(`input[name=${element}]:checked`).prop("checked", false);
                $(`input[name=${element}][checked=checked]`).prop("checked", true);
            }
            );
            // function called to revert view changes on app drawer body background and color theme
            this._PlResetDirtyData(pl_session, pl_splitter)
            this._plColorThemeCancel();
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
                } else if(index && self.pl_dirty_data[index].data('field-save') && self.pl_dirty_data[index] && (self.pl_dirty_data[index].data('field-save')in pl_session && self.pl_dirty_data[index].hasClass('pl_cancel_radio'))){
                    $('input[name=' + self.pl_dirty_data[index].attr('name') + '][data-value="' + pl_session[self.pl_dirty_data[index].data('field-save')] + '"]').prop('checked', true);
                }
            }
            self.pl_dirty_data = {}
        },

        _plColorThemeEdit: function(ev) {
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
                var pl_edit_section = QWeb.render("pl_theme_edit_section_company", {
                    pl_theme_data: arg[0],
                });
                $("div#company_theme_edit_section").html(pl_edit_section);
                self._scrollToDown();
            });
        },

        _scrollToDown: function() {
            // Scroll down div
            $("div.pl_color_theme_qweb_div_company").scrollTop($("div.pl_color_theme_qweb_div_company")[0].scrollHeight);
        },

        _plCustomColorThemeAdd: function() {
            var self = this;
            var pl_edit_section = QWeb.render("pl_theme_edit_section_company", {
                pl_theme_data: {},
            });
            $("div#company_theme_edit_section").html(pl_edit_section);
            self._scrollToDown();
        },

        _plColorThemeCancel: function() {
            $("div#company_theme_edit_section").html("");
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

        _pl_get_theme_data_dict: function() {
            var pl_data = {};
            this.pl_company_theme_fields.forEach((pl_element)=>{
                pl_data[pl_element] = $(`input#${pl_element}_company`).val();
            }
            );
            return pl_data;
        },

        _plColorThemeSave: function() {
            var self = this;
            var pl_theme_data = this._pl_get_theme_data_dict();
            pl_theme_data["pl_company"] = self.pl_form_id;
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
                    var color_theme_temp = QWeb.render("pl_color_theme_qweb_template_company", {
                        widget: self,
                    });
                    $("div.pl_color_theme_qweb_div_company").html(color_theme_temp);
                });
            });
        },

        _plColorThemeDelete: function(ev) {
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
                            var color_theme_temp = QWeb.render("pl_color_theme_qweb_template_company", {
                                widget: self,
                            });
                            $("div.pl_color_theme_qweb_div_company").html(color_theme_temp);
                        });
                    },
                });
            }
        },

        _plRemoveTheme: function(pl_theme_id) {
            var result = false;
            var pl_custom_themes = _.filter(this.data.pl_color_theme.custom, function(theme) {
                return pl_theme_id != theme.id;
            });
            this.data.pl_color_theme.custom = pl_custom_themes;
            return result;
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
                    var color_theme_temp = QWeb.render("pl_color_theme_qweb_template_company", {
                        widget: self,
                    });
                    $("div.pl_color_theme_qweb_div_company").html(color_theme_temp);
                });
            });
        },

        _updateThemeData: function(updated_data) {
            var pl_updated_data = _.map(this.data.pl_color_theme.custom, function(theme) {
                if (theme.id == updated_data.id)
                    return updated_data;
                else
                    return theme;
            });
            this.data.pl_color_theme.custom = pl_updated_data;
        },

        on_detach_callback: function() {
            this._plColorThemeCancel();
        },
    });

    widgetRegistry.add("pl_company_config_widget", PlCompanyConfigWidget);

    return PlCompanyConfigWidget;
});
