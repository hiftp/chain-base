odoo.define("pl_curved_backend_theme.pl_appdrawer_edit", function (require) {
  "use strict";

  var Widget = require("web.Widget");
  var SystrayMenu = require("web.SystrayMenu");

  var PlAppdrawerEdit = Widget.extend({
    template: "pl_appdrawer_edit",
    events: {
      "click #pl_customize_appdrawer": "_plShowFavIcons",
    },
    sequence: 59,
    init: function () {
      var self = this;
      this._super.apply(this, arguments);
    },

    _plShowFavIcons: function (ev) {
      ev.preventDefault();
      var self = this;
      document.body.classList.add("pl_appsmenu_edit");

      $("div.pl_appdrawer_inner_app_div")
        .find("span.pl_fav_icon")
        .removeClass("d-none");
      $("div.pl_appdrawer_div")
        .find("div.pl-app-drawer-close")
        .removeClass("d-none");

      $("div.pl_appdrawer_inner_app_div")
        .find("div.dropdown-item")
        .each((app_div, item) => {
          if ($(item).find("span.pl_rmv_fav").length) {
            $(item).addClass("pl_add_visible");
          }
        });
    },
  });

//  PlAppdrawerEdit.prototype.sequence = 6;
  SystrayMenu.Items.push(PlAppdrawerEdit);

  return {
    PlAppdrawerEdit: PlAppdrawerEdit,
  };
});
