odoo.define('organisation.calendar_div', function (require) {
    "use strict";

    console.log("Calendar div");
    $(document).ready(function () {
        $(".fc-daygrid-event-harness").on('click', function(event){
            $("#show_elements").addClass("show_calendar");
//            $("#show_elements").css({
//                top: event.pageY+100,
//                left: event.pageX+100
//              });
//            console.log(event.pageY);
//            console.log(event.pageX);
//            console.log($(this).innerText);
            var title = $(this).children()[0].fcSeg.eventRange.def.title;
//            console.log(title);
            var all_list = eval(c_events.value);
//            console.log(all_list);
            var needed_list = null;
            for (var i = 0; i < all_list.length; i++){
                console.log(all_list[i]);
                if (all_list[i].title == title){
                    needed_list = all_list[i];
                }
            }
//            console.log(needed_list);
            $('#title').val(needed_list.title)
            $('#start_date_time').val(new Date(needed_list.start));
            $('#end_date_time').val(new Date(needed_list.end));

        });

        $("#close").on('click', function(event){
            $("#show_elements").toggleClass("show_calendar");
        });

    });
});