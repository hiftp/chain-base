odoo.define("pl_curved_backend_theme.FormController", function(require) {
    "use strict";

    var PlFormController = require("web.FormController");
    var PlFormRenderer = require("web.FormRenderer");
    var Session = require("web.session");
    var ajax = require("web.ajax");

    PlFormRenderer.include({
        events: _.extend({}, PlFormRenderer.prototype.events, {
            "dblclick .o_form_sheet_bg": "_plOnFormviewDblClick",
            //      "click span.phone-sm-btns": "_plToggleStatusButton",
        }),

        //    init: function (parent, state, params) {
        //        this._super.apply(this, arguments);
        //        $(document).on("click", function (event) {
        //            var $trigger = $(".phone-sm-btns");
        //            if ($trigger !== event.target && !$trigger.has(event.target).length) {
        //              $(".o_statusbar_buttons").removeClass("show");
        //            }
        //          });
        //    },

        _updateView: function($newContent) {
            this._super(...arguments);
            var temp_this = this;
            if (this.$el.children(".o_FormRenderer_chatterContainer").length) {
                this._rpc({
                    model: "pl.global.config",
                    method: "pl_get_value_from_scope",
                    args: [["pl_chatter"]],
                }).then(function(result) {
                    if (result.pl_chatter && result.pl_chatter == "pl_chatter_right") {
                        //If chatter is write we have to give resizable option
                        temp_this.$el.addClass("pl-right-content");
//                        if (Session['pl_split_view'] != 'vertical') {
                        if (result && result.pl_chatter == 'pl_chatter_right') {
                            $('<div class="custom_seperator"></div>').insertAfter(temp_this.$el.find('.o_form_sheet_bg'));
                            if (Session['pl_lang_direction'] && Session['pl_lang_direction'] == 'rtl') {
                                $('.custom_seperator').draggable({
                                    axis: 'x',
                                    containment: 'parent',
                                    helper: 'clone',
                                    start: function(event, ui) {
                                        $(this).attr('start_offset', $(this).offset().left);
                                        $(this).attr('start_next_height', $(this).prev().width());
                                    },
                                    drag: function(event, ui) {
                                        $('.custom_seperator').css({
                                            'opacity': '0.2'
                                        })
                                        var next_element = $(this).prev();
                                        var prev_element = $(this).next();
                                        var y_difference = $(this).attr('start_offset') - ui.offset.left;
                                        prev_element.width(ui.offset.left - prev_element.offset().left);
                                        next_element.width(parseInt($(this).attr('start_next_height')) + y_difference);
                                    }

                                });
                            } else {
                                $('.custom_seperator').draggable({
                                    axis: 'x',
                                    containment: 'parent',
                                    helper: 'clone',
                                    start: function(event, ui) {
                                        $(this).attr('start_offset', $(this).offset().left);
                                        $(this).attr('start_next_height', $(this).next().width());
                                    },
                                    drag: function(event, ui) {
                                        var prev_element = $(this).prev();
                                        $('.custom_seperator').css({
                                            'opacity': '0.2'
                                        })
                                        var next_element = $(this).next();
                                        var y_difference = $(this).attr('start_offset') - ui.offset.left;
                                        prev_element.width(ui.offset.left - prev_element.offset().left);
                                        //                            next_element.width(parseInt($(this).attr('start_next_height'))+y_difference);
                                    }

                                });
                            }
                            $('.custom_seperator').on("dragstop", function(event, ui) {
                                $('.custom_seperator').css({
                                    'opacity': '1'
                                })
                                ajax.jsonRpc("/pl_curved_backend_theme/save/form_width", "call", {
                                    val: isNaN(parseFloat($('.o_form_sheet_bg').width())) ? false : parseFloat($('.o_form_sheet_bg').width())
                                });
                            });
                            if (Session['pl_form_view_width']) {
                                temp_this.$el.find('.o_form_sheet_bg').css({
                                    'width': Session['pl_form_view_width']
                                })
                                //                temp_this.$el.find('.o_FormRenderer_chatterContainer').css({'width':Session['pl_form_view_width']})
                            } else {
                                temp_this.$el.find('.o_form_sheet_bg').outerWidth('60%');
                            }
                        }
                    }
                });
            }
        },

        _plOnFormviewDblClick: function(ev) {
            var $target = $(ev.target);
            var temp_this = this;
            this._rpc({
                model: "pl.global.config",
                method: "pl_get_value_from_scope",
                args: [["pl_click_edit"]],
            }).then(function(result) {
                if (result.pl_click_edit && temp_this.mode == "readonly" && !$target.is(".o_form_label, .o_field_widget") && Session.pl_curved_backend_theme_data) {
                    temp_this.getParent()._plOnClickEditMode();
                }
            });
        },

        _renderTagHeader: function(node) {
            const $statusbar = this._super.apply(this, arguments);
            // Collapse statusbar buttons on mobile devices.
            // Check if status button is more than 1 then enable dropdown.
            if ($statusbar.find("button:not(.o_invisible_modifier)").length > 0) {
                return $statusbar.prepend($('<span class="phone-sm-btns"><i class="fa fa-cog"></i> Action</span>').bind('click', function(ev) {
                    $(".o_statusbar_buttons").toggleClass("show");
                }));
            }

            return $statusbar;
        },

        _plToggleStatusButton: function(ev) {
            $(".o_statusbar_buttons").toggleClass("show");
        },
    });

    PlFormController.include({
        custom_events: _.extend({}, PlFormController.prototype.custom_events, {
            pl_click_to_edit: "_plOnClickEditMode",
        }),
        _plOnClickEditMode: function(ev) {
            if (this.is_action_enabled("edit")) {
                this._setMode("edit");
            }
        },
    });
});
