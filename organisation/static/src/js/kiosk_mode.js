odoo.define('hr_attendance.kiosk_mode_organisation', function (require) {
"use strict";

const KioskMode = require('hr_attendance.kiosk_mode');
const KioskConfirm = require('hr_attendance.kiosk_confirm');
var ajax = require('web.ajax');
var core = require('web.core');
var Session = require('web.session');
var field_utils = require('web.field_utils');
var QWeb = core.qweb;

KioskMode.include({
    events: {
        "click .o_hr_attendance_button_submit": function() {
            var secret_pin = $("input[id='badge_id']").val();
            ajax.jsonRpc('/get_employee_kiosk_values', 'call',{'member_id': secret_pin})
            .then((result) => {
                var action = {
                type: 'ir.actions.client',
                name: 'Confirm',
                tag: 'hr_attendance_kiosk_confirm',
                employee_id: parseInt(result.employee_id),
                employee_name: result.employee_name,
                employee_state: result.employee_state,
                employee_hours_today: result.employee_hours_today,
                };
                this.do_action(action);
            });
        },
//        "click .o_hr_attendance_button_view_vehicle": function() {
//            $('#vehicle_registration_selection option').remove();
//            $('#vehicle_registration_selection').append($('<option>',
//                {
//                   text : "Select..."
//                }));
//            var secret_pin = $("input[id='badge_id']").val();
//            ajax.jsonRpc('/get_employee_vehicles', 'call',{'secret_pin': secret_pin})
//            .then((result) => {
//                console.log(result)
//                if(result.length > 0){
//                for (var i=0; i<result.length; i++){
//                    $('#vehicle_registration_selection').append($('<option>',
//                    {
//                       value: result[i].id,
//                       text : result[i].name
//                    }));
//                }
//                }
//                else{
//                    $('#vehicle_registration_selection').append($('<option>',
//                    {
//                       text : "No Matches Found!"
//                    }));
//                }
//            });
//        },
    },
});

KioskConfirm.include({

    events: {
        "click .o_hr_attendance_back_button": function () { this.do_action(this.next_action, {clear_breadcrumbs: true}); },
        "click .o_hr_attendance_sign_in_out_icon": _.debounce(function () {
            var self = this;
            var veh_registration = $("select[id='vehicle_registration_selection']").val();

            this._rpc({
                    model: 'hr.employee',
                    method: 'attendance_manual',
                    args: [[this.employee_id], this.next_action, veh_registration],
                })
                .then(function(result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                    }
                });
        }, 200, true),
    },

    start: function () {
        var self = this;
        this.getSession().user_has_group('hr_attendance.group_hr_attendance_use_pin').then(function(has_group){
            self.use_pin = has_group;
            self.$el.html(QWeb.render("HrAttendanceKioskConfirm", {widget: self}));
            self.start_clock();
        });
        var employee_id = self.employee_id
        ajax.jsonRpc('/get_employee_vehicles', 'call',{'employee_id': employee_id})
        .then((result) => {
                if(result.length > 0){
//                $('#vehicle_registration_selection').append($('<option>',
//                    {
//                       text : "Select..."
//                    }));
                for (var i=0; i<result.length; i++){
                    $('#vehicle_registration_selection').append($('<option>',
                    {
                       value: result[i].id,
                       text : result[i].name
                    }));
                }
                }
                else{
                    $('#div_vehicle_registration').append('<span><h3><small>You have no vehicle registered!</small></h3></span>');
                    var element = document.getElementById("vehicle_registration_selection");
                    if (element){
                        element.setAttribute("disabled", "1");
                    }
                }
            });

        return self._super.apply(this, arguments);
    },
    });
});