odoo.define('pl_curved_backend_theme.PlActionManagerInherit', function(require) {
    "use strict";

    var ActionManager = require('web.ActionManager');
    var core = require('web.core');
    var dom = require('web.dom');
    var session = require("web.session");
    var ajax = require("web.ajax");
    ActionManager.prototype.className = 'o_action_manager split_div'

    ActionManager.include({
        init: function() {
            var res = this._super.apply(this, arguments);
            this.pl_controller_stack = []
        },

        _onHistoryBack: function() {
            // Overrided to destroy controllers except list view when all the records are deleted
            if (this.currentDialogController) {
                this._closeDialog();
            } else {
                var controller_length = this.controllerStack.length;
                if (session['pl_split_view'] && session['pl_split_view'] != 'no_split' && this.pl_controller_stack && this.pl_controller_stack.length && controller_length == 1) {
                    this._restoreController(this.controllerStack[0]);
                } else if (controller_length > 1) {
                    this._restoreController(this.controllerStack[controller_length - 2]);
                }
            }
        },

        _pushController: function(controller) {
            // Overrided to stop the list controller that is destroyed whenever a form view is opened in split view and for adding separators
            var self = this;
            //          Checking here if we have to split the view or not
            if (!session['pl_split_view'] || session['pl_split_view'] == 'no_split' || controller.viewType != 'form' || !this.getCurrentController() || self.getCurrentController()['viewType'] != 'list' || (this.actions[controller['actionID']].res_model != this.actions[this.getCurrentController()['actionID']].res_model)) {
                if (controller.viewType == 'list' && !controller.widget.$el.find('.o_list_view').hasClass('Pl_list_view'))
                    controller.widget.$el.find('.o_list_view').addClass('Pl_list_view')
                // detach the current controller
                if (self.pl_controller_stack && self.pl_controller_stack.length) {
                    self.PlPrevControllers();
                    $('body').removeClass('pl_splitter horizontal-split');
                    if ($('#separator').length)
                        $('#separator').remove()
                }
                this._detachCurrentController();

                // push the new controller to the stack at the given position, and
                // destroy controllers with an higher index
                var toDestroy = this.controllerStack.slice(controller.index);
                // reject from the list of controllers to destroy the one that we are
                // currently pushing, or those linked to the same action as the one
                // linked to the controller that we are pushing
                toDestroy = _.reject(toDestroy, function(controllerID) {
                    return controllerID === controller.jsID || self.controllers[controllerID].actionID === controller.actionID;
                });
                this._removeControllers(toDestroy);
                this.controllerStack = this.controllerStack.slice(0, controller.index);
                this.controllerStack.push(controller.jsID);
                // append the new controller to the DOM
                this._appendController(controller);
            } else {
                if ($('#separator').length) {
                    $('#separator').remove();
                }
                $('.pl_splitted_page').insertBefore('<div id="separator"></div>');
                if (session['pl_split_view'] && session['pl_split_view'] == 'horizontal')
                    $('body').addClass('pl_splitter horizontal-split');
                else if (session['pl_split_view'] && session['pl_split_view'] == 'vertical')
                    $('body').addClass('pl_splitter');

                self.pl_controller_stack.push(controller.jsID);
                // append the new controller to the DOM
                this._appendController(controller, this.$el.children('.o_action').find('.o_content'));
            }

            // notify the environment of the new action
            this.trigger_up('current_action_updated', {
                action: this.getCurrentAction(),
                controller: controller,
            });

            // close all dialogs when the current controller changes
            core.bus.trigger('close_dialogs');

            // toggle the fullscreen mode for actions in target='fullscreen'
            this._toggleFullscreen();
        },

        _appendController: function(controller, custom_ele_=false) {
            // Overrided to hide controlpanel on form view and to add resizable.
            if (custom_ele_ && custom_ele_.length) {
                if ($('.pl_splitted_page').length)
                    $('.pl_splitted_page').remove();
                controller.widget.$el.find('.o_control_panel').find('.o_cp_top').addClass('d-none');
                controller.widget.$el.find('.o_control_panel').find('.o_cp_bottom').find('.o_cp_bottom_right').addClass('d-none');
                dom.append(custom_ele_, controller.widget.$el, {
                    in_DOM: this.isInDOM,
                    callbacpl: [{
                        widget: controller.widget
                    }],
                });
                var options = {
                    containment: 'parent',
                    helper: 'clone'
                }
                if (session['pl_split_view'] && session['pl_split_view'] == 'vertical') {
                    if (session['pl_splitted_vertical_width'])
                        this.getCurrentController().widget.$el.find('.Pl_list_view').outerWidth(session['pl_splitted_vertical_width'])
                    if (session['pl_lang_direction'] && session['pl_lang_direction'] == 'rtl') {
                        Object.assign(options, {
                            axis: 'x',
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
                        })
                    } else {
                        Object.assign(options, {
                            axis: 'x',
                            start: function(event, ui) {
                                $(this).attr('start_offset', $(this).offset().left);
                                $(this).attr('start_next_height', $(this).next().width());
                            },
                            drag: function(event, ui) {
                                $('.custom_seperator').css({
                                    'opacity': '0.2'
                                })
                                var prev_element = $(this).prev();
                                var next_element = $(this).next();
                                var y_difference = $(this).attr('start_offset') - ui.offset.left;
                                prev_element.width(ui.offset.left - prev_element.offset().left);
                                //                                next_element.width(parseInt($(this).attr('start_next_height')) + y_difference);
                            }
                        })
                    }
                    $('<div id="separator" class="custom_seperator"></div>').insertAfter(this.getCurrentController().widget.$el.find('.Pl_list_view'));
                } else {
                    if (session['pl_splitted_horizontal_height'])
                        this.getCurrentController().widget.$el.find('.Pl_list_view').outerHeight(session['pl_splitted_horizontal_height'])
                    Object.assign(options, {
                        axis: 'y',
                        start: function(event, ui) {
                            $(this).attr('start_offset', $(this).offset().top);
                            $(this).attr('start_next_height', $(this).next().height());
                        },
                        drag: function(event, ui) {
                            var prev_element = $(this).prev();
                            var next_element = $(this).next();
                            var y_difference = $(this).attr('start_offset') - ui.offset.top;
                            prev_element.height(ui.offset.top - prev_element.offset().top);
                            next_element.height(parseInt($(this).attr('start_next_height')) + y_difference);
                            $('.resize-hr').css({
                                'opacity': '0.2'
                            })
                        }
                    });
                    $('<div id="separator" class="resize-hr"></div>').insertAfter(this.getCurrentController().widget.$el.find('.Pl_list_view'));
                }
                $('#separator').draggable(options);
                $('#separator').on("dragstop", function(event, ui) {
                    if (session['pl_split_view'] == 'vertical') {
                        $('.custom_seperator').css({
                            'opacity': '1'
                        })
                        var val = {
                            'pl_split_vertical_list_width': isNaN(parseFloat($('.Pl_list_view').outerWidth(true))) ? false : parseFloat($('.Pl_list_view').outerWidth(true)),
                        }
                    } else {
                        $('.resize-hr').css({
                            'opacity': '1'
                        })
                        var val = {
                            'pl_split_horizontal_list_height': isNaN(parseFloat($('.Pl_list_view').outerHeight(true))) ? false : parseFloat($('.Pl_list_view').outerHeight(true)),
                        }
                    }
                    ajax.jsonRpc("/pl_curved_backend_theme/save/pl_splitted_form_width", "call", {
                        'data': val
                    });
                });

            } else {
                controller.widget.$el.find('.o_list_view').css("width", "");
                controller.widget.$el.find('.o_list_view').css("height", "");
                dom.append(this.$el, controller.widget.$el, {
                    in_DOM: this.isInDOM,
                    callbacpl: [{
                        widget: controller.widget
                    }],
                });
            }
            if (controller.scrollPosition) {
                this.trigger_up('scrollTo', controller.scrollPosition);
            }
        },

        PlPrevControllers: function() {
            let self = this;
            _.map(_.uniq(self.pl_controller_stack), function(re) {
                var currentController = self.controllers[re];
                if (currentController) {
                    currentController.scrollPosition = self._getScrollPosition();
                    dom.detach([{
                        widget: currentController.widget
                    }]);
                }
            });
            self.pl_controller_stack = [];
        },
    });

});
