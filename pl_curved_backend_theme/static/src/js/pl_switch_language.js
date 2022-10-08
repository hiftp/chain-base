odoo.define("pl_curved_backend_theme.pl_switch_language", function (require) {
  "use strict";

  var SystrayMenu = require("web.SystrayMenu");
  var Widget = require("web.Widget");
  var ajax = require("web.ajax");
  var session = require("web.session");

  var PlSwitchLanguage = Widget.extend({
    template: "pl_switch_language",
    events: {
      "click .pl_toggle_language": "_plToggleLanguageClick",
    },
    sequence: 3,

    willStart: async function () {
      const _super = this._super.bind(this);
      const data = await this._rpc({
        route: "/get/installed/languages",
      });
      this.languages = data;
      this.current_language = String(session.user_context.lang);
      return _super(...arguments);
    },

    _plToggleLanguageClick: function (ev) {
      var self = this;
      var selected_language = $(ev.currentTarget).data("language-code");
      ajax
        .jsonRpc("/selected/language", "call", {
          selected_language: selected_language,
        })
        .then(function () {
          self.do_action("reload_context");
        });
    },
  });

  SystrayMenu.Items.push(PlSwitchLanguage);
  return PlSwitchLanguage;
});
