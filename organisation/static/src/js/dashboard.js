odoo.define('organisation.dashboard', function(require){
    "use strict";
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
//    $(document).on('click',"#multi_upload_submit",function() {
//        var name = $("input[id='document_name']").val();
//        var description = $("input[id='document_description']").val();
//        var document = $("input[id='document_file']").val();
//        if(name && description && document){
//            alert("Document uploaded successfully")
//        }
//    });

    $(document).ready(function(){
    var type_selected = $("select[name='type']").val();
    if(type_selected == 'group'){
        var group_id = $("select[name='group_id']").val();
        ajax.jsonRpc('/get_athletes_list', 'call',{'group_id': group_id})
        .then(function (result) {
            $('#group_athletes tbody').empty();
            for (var i=0; i<result.vals.length; i++){
                $('#group_athletes tbody').append('<tr><td style="vertical-align: top; width: 168px;">' + result.vals[i].name + '<td style="vertical-align: top; width: 168px;">' + result.vals[i].email + '</td><td style="vertical-align: top; width: 168px;">' + result.vals[i].phone + '</td>');
                }
        });
        $('#add_athlete').hide();
        $('#add_group').show();
        $('#athlete_list').show();
    }
    if(type_selected == 'athlete'){
        $('#add_athlete').show();
        $('#add_group').hide();
        $('#athlete_list').hide();
    }
    var count = 1
    $("input[id='athletes_count']").val(count);
    var athlete_count = document.querySelectorAll('.athlete-counter').length;
    localStorage.setItem('athlete_count',athlete_count);
    $('#add_athlete_button').click(function() {
        count++;
        $("input[id='athletes_count']").val(count);
        var athlete_id = "athlete_id" + athlete_count;
        var athlete = "athlete" + athlete_count;
        var str_athletes = $("input[id='select_athletes_list']").val();
        var athletes = eval(str_athletes)
        var add_athlete_temp = `<div id="${athlete_id}" class="athlete-counter">
                                <hr/>
                                <div class="form-group col-12 s_website_form_field s_website_form_required s_website_form_custom"
                                data-type="char" data-name="Field">
                                    <div class="row s_col_no_resize s_col_no_bgcolor">
                                        <label class="col-form-label col-sm-auto s_website_form_label"
                                        style="width: 200px" for="${athlete}">
                                            <span class="s_website_form_label_content">Athlete: </span>
                                            <span class="s_website_form_mark"> *</span>
                                        </label>
                                        <div class="col-sm">
                                             <select id="${athlete}" type="text" class="form-control s_website_form_input" name="${athlete}" required="">
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            </div>`
        $('#div_add_athlete').append(add_athlete_temp);
        var selEl = document.getElementById(athlete);
//        for (var i=0; i<athletes.length; i++){
//            selEl.append($('<option>',
//             {
//                value: athletes[i].id,
//                text : athletes[i].name
//             }));
//         }
        var selEl_id = '#'
        var selEl_id = selEl_id.concat(athlete);
        for (var i=0; i<athletes.length; i++){
            $(selEl_id).append($('<option>',
             {
                value: athletes[i].id,
                text : athletes[i].name
             }));
         }
        athlete_count++;
        localStorage.setItem('athlete_count',athlete_count);
        });


    $('#remove_athlete_button').click(function() {
    if (athlete_count > 1)
        {
            athlete_count--;
            count--;
            $("input[id='athletes_count']").val(count);
            $('#' + ("athlete_id" + athlete_count)).remove();
            localStorage.setItem('athlete_count',athlete_count);
        }
        });
    var task_id = $("input[id='task_id']").val();
    var athlete_task_id = $("input[id='athlete_task_id']").val();
    if(task_id){
        $('#portal_action_task_start').show();
        $('#portal_action_task_end').hide();
        }
    if(athlete_task_id){
        $('#portal_action_athlete_task_start').show();
        $('#portal_action_athlete_task_end').hide();
        }
    });

    publicWidget.registry.Dashboard = publicWidget.Widget.extend({
        selector: '#portal_task_buttons',
        events: {
               'click #portal_action_task_start': '_onClickTaskStart',
               'click #portal_action_task_end': '_onClickTaskEnd',
    },
     _onClickTaskStart: function (ev) {
        var task_id = $("input[id='task_id']").val();
        ajax.jsonRpc('/start_task', 'call',{'task_id': task_id})
                .then(function (result) {
                    $('#portal_action_task_start').hide();
                    $('#portal_action_task_end').show();
                });
     },
     _onClickTaskEnd: function (ev) {
        var task_id = $("input[id='task_id']").val();
        ajax.jsonRpc('/end_task', 'call',{'task_id': task_id})
                .then(function (result) {
                    $('#portal_action_task_start').show();
                    $('#portal_action_task_end').hide();
                });
     },

    });

    publicWidget.registry.AthleteTaskDashboard = publicWidget.Widget.extend({
        selector: '#portal_athlete_task_buttons',
        events: {
               'click #portal_action_athlete_task_start': '_onClickAthleteTaskStart',
               'click #portal_action_athlete_task_end': '_onClickAthleteTaskEnd',
    },
     _onClickAthleteTaskStart: function (ev) {
        var task_id = $("input[id='athlete_task_id']").val();
        ajax.jsonRpc('/start_athlete_task', 'call',{'task_id': task_id})
                .then(function (result) {
                    $('#portal_action_athlete_task_start').hide();
                    $('#portal_action_athlete_task_end').show();
                });
     },
     _onClickAthleteTaskEnd: function (ev) {
        var task_id = $("input[id='athlete_task_id']").val();
        ajax.jsonRpc('/end_athlete_task', 'call',{'task_id': task_id})
                .then(function (result) {
                    $('#portal_action_athlete_task_start').show();
                    $('#portal_action_athlete_task_end').hide();
                });
     },

    });

    publicWidget.registry.TaskChecklist = publicWidget.Widget.extend({
        selector: '.checklist_button',
        events: {
               'click .checklist_button': '_onClickChecklistComplete',
    },
     _onClickChecklistComplete: function (ev) {
        window.location.reload();
     },

    });

    publicWidget.registry.Attendance = publicWidget.Widget.extend({
        selector: '#attendance_buttons',
        events: {
               'click #button_sign_in': '_onClickSignIn',
               'click #button_sign_out': '_onClickSignOut',
    },
     _onClickSignIn: function (ev) {
        this.do_action({
            type: 'ir.actions.client',
            tag: 'hr_attendance_kiosk_mode',
            mode: 'fullscreen',

        });
     },
     _onClickSignOut: function (ev) {

     },

    });

    publicWidget.registry.Document = publicWidget.Widget.extend({
        selector: '#document_type_selection',
        events: {
               'change #document_type': '_onChangeType',
    },
     _onChangeType: function (ev) {
            var type_selected = $("select[name='type']").val();
            if(type_selected == 'group'){
                $('#add_athlete').hide();
                $('#add_group').show();
                $('#athlete_list').show();
                var group_id = $("select[name='group_id']").val();
//                ajax.jsonRpc('/get_athletes_list', 'call',{'group_id': group_id})
//                console.log(result)
//                .then(function (result) {
//                    console.log(result)
//
//                });
            }
            if(type_selected == 'athlete'){
                $('#add_athlete').show();
                $('#add_group').hide();
                $('#athlete_list').hide();
            }

     },


    });

    publicWidget.registry.Group = publicWidget.Widget.extend({
        selector: '#athlete_group_selection',
        events: {
               'change #athlete_group_selected': '_onChangeGroup',
    },
     _onChangeGroup: function (ev) {
            var group_id = $("select[name='group_id']").val();
            ajax.jsonRpc('/get_athletes_list', 'call',{'group_id': group_id})
            .then(function (result) {
                $('#group_athletes tbody').empty();
                for (var i=0; i<result.vals.length; i++){
                    $('#group_athletes tbody').append('<tr><td style="vertical-align: top; width: 168px;">' + result.vals[i].name + '<td style="vertical-align: top; width: 168px;">' + result.vals[i].email + '</td><td style="vertical-align: top; width: 168px;">' + result.vals[i].phone + '</td>');
                    }
            });

     },


    });
});