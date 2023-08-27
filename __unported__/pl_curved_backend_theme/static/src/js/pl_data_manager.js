odoo.define("pl_curved_backend_theme.DataManager", function (require) {
  "use strict";

  var DataManager = require("web.DataManager");
  var session = require("web.session");
  DataManager.include({
    load_views: async function ({ model, context, views_descr }, options = {}) {
      // Hide/close app drawer when new view is loaded.
      let pl_url_hash = window.location.hash;
      if (
        document.body.classList.contains("pl_appsmenu_active") &&
        (pl_url_hash.includes("action") || pl_url_hash.includes("model"))
      ) {
        setTimeout(function () {
          document.body.classList.toggle("pl_appsmenu_active");
          document.body.classList.remove("brightness");

          if (session.pl_current_color_mode == "pl-light") {
            // Apply Color theme back.
            document.body.style.setProperty(
              "--body-background",
              session.pl_color_theme["body-background"]
            );

            document.body.style.setProperty(
              "--nav-link-color",
              session.pl_color_theme["nav-link-color"]
            );

            document.body.style.setProperty(
              "--pl-over-link",
              session.pl_color_theme["pl-over-link"]
            );
          }
          if (session.pl_color_theme.pl_header_icon_clr) {
            $("div.o_menu_systray").addClass("pl_color_theme_dark_header");
            $('.o_main_navbar button.phone-menu-btn').addClass("pl_color_theme_dark_header");
            $('.pl_left_sidebar_panel .pl_app_sidebar .inner-sidebar button.phone-menu-btn').addClass("pl_color_theme_dark_header");
          }
        }, 1000);
        $("html").attr("data-color-mode", session.pl_current_color_mode);
      }
      return this._super({ model, context, views_descr }, options);
    },
  });

  return DataManager;
});
