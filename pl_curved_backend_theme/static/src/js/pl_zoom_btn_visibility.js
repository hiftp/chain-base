odoo.define('pl_curved_backend_theme.PlZoomBtnVisibility', function (require) {
"use strict";

    window.onhashchange = function() {
        if ($(".o_content").length && document.querySelector(".o_content div:last-child")) {
            if ($(".pl-zoom-view").hasClass('d-none'))
                $(".pl-zoom-view").removeClass('d-none');

            document
                .querySelector(".o_content div:last-child")
                .removeAttribute("style");
                if (document.querySelector(".pl-zoom-per"))
                    document.querySelector(".pl-zoom-per").innerText = "100%";
        }
        else{
            if ($(".pl-zoom-view").length){
                $(".pl-zoom-view").addClass('d-none');
            }
        }
    }
});