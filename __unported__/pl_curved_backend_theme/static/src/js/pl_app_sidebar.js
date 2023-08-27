odoo.define("pl_curved_backend_theme.pl_app_sidebar", function (require) {
  "use strict";

  var Widget = require("web.Widget");
  const ajax = require("web.ajax");

  var plAppsBar = Widget.extend({
    template: "pl_curved_backend_theme.side_appbar",
    events: _.extend({}, Widget.prototype.events, {
      "click .pl_app": "_plAppClicked",
      "click .left_sidebar_arrow": "_plToggleVerticalMenus",
    }),
    /**
     * @override
     * @param {web.Widget} parent
     * @param {Object} menuData
     * @param {Object[]} menuData.children
     */
    init: function (parent, menuData) {
      this._super.apply(this, arguments);
      this._activeApp = undefined;
      this._pl_fav_bar = parent.pl_favorite_bar;
      this.parent = parent;
      this._apps = menuData;
    },

    willStart: async function () {
      const _super = this._super.bind(this);
      var pl_fav_apps = [];
      await ajax
        .jsonRpc("/pl_curved_theme/get_fav_icons", "call", {
          pl_app_icons: this._apps,
        })
        .then(function (data) {
          pl_fav_apps = data;
        });
      this._apps = pl_fav_apps;
    },

    start: function () {
      var temp_this = this;
      this._setActiveApp(this.parent.menuService.getCurrentApp());
      return this._super.apply(this, arguments).then(function () {
        // if (
        //   !document.body.classList.contains("pl_vertical_body_panel") &&
        //   !temp_this.$el.children(".pl_app_sidebar_menu").children().length
        // ) {
        //   temp_this.$el.parents(".pl_left_sidebar_panel").addClass("d-none");
        // } else {
        //   temp_this.$el.parents(".pl_left_sidebar_panel").removeClass("d-none");
        // }
      });
    },

    /**
     * @returns {Object[]}
     */
    getApps: function () {
      return this._apps;
    },

    fav_bar_menu: function () {
      return this._pl_fav_bar;
    },
    /**
     * @private
     * @param {Object} app
     */
    _openApp: function (app) {
      this._setActiveApp(app);
      this.parent.menuService.selectMenu(app.id);
    },
    /**
     * @private
     * @param {Object} app
     */
    _setActiveApp: function (menuID) {
      if (this.$el){
        var $oldActiveApp = this.$(".pl_app.active");
        $oldActiveApp.removeClass("active");
        var $newActiveApp = this.$('.pl_app[data-menu-id="' + menuID.id + '"]');
        $newActiveApp.addClass("active");
      }
    },
    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Called when clicking on an item in the apps menu.
     *
     * @private
     * @param {MouseEvent} ev
     */
    _plAppClicked: function (ev) {
      var $target = $(ev.currentTarget);
      var actionID = $target.data("action-id");
      var menuID = $target.data("menu-id");
      var app = _.findWhere(this._apps, {
        actionID: actionID,
        id: menuID,
      });
      this._openApp(app);
      ev.preventDefault();
      $target.blur();
    },
    _plToggleVerticalMenus: function () {
      document.body.classList.toggle("pl_verticalmenus_expanded");
    },
  });

  return plAppsBar;
});
