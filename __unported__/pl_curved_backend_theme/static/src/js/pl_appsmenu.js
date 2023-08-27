odoo.define("pl_curved_backend_theme.pl_appsmenu", function (require) {
  "use strict";

  var session = require("web.session");
  var config = require("web.config");
  var core = require("web.core");
  var QWeb = core.qweb;
  var { NavBar } = require("@web/webclient/navbar/navbar");
  var { patch } = require("web.utils");
  const { useListener } = require("web.custom_hoopl");
  var plAppSidebar = require("pl_curved_backend_theme.pl_app_sidebar");
  const ajax = require("web.ajax");

  function pl_GetReducedMenuData(memo, menu) {
    if (menu.actionID) {
      var key = menu.pl_parent_name ? menu.pl_parent_name : "";
      menu["pl_title"] = (key + menu.name).toLowerCase();
      memo[key + menu.name] = menu;
    }
    if (menu.children.length) {
      var child_menus = this.menuService.getMenuAsTree(menu.id).childrenTree;
      child_menus.forEach((child_menu) => {
        child_menu["pl_parent_id"] = menu.id;
        if (menu["pl_parent_name"]) {
          child_menu["pl_parent_name"] =
            menu["pl_parent_name"] + "/" + menu.name;
        } else {
          child_menu["pl_parent_name"] = menu.name;
        }
      });
      _.reduce(child_menus, pl_GetReducedMenuData.bind(this), memo);
    }
    return memo;
  }

  // todo: Resolve the commented code inside the patch (make compatible with v15)

  patch(NavBar.prototype, "pl_curved_backend_theme.pl_appsmenu", {
    setup() {
      this._super();
      useListener(
        "keydown",
        ".pl_menu_search_box input",
        this._plSearchValuesMovement
      );
      useListener(
        "input",
        ".pl_menu_search_box input",
        this._plSearchMenuListTime
      );
      useListener(
        "click",
        ".pl-menu-search-value",
        this._plSearchValuesSelecter
      );
      useListener("shown.bs.dropdown", this._plSearchFocus);
      useListener("hidden.bs.dropdown", this._plSearchResetvalues);
      useListener("hide.bs.dropdown", this._plHideAppsMenuList);
      useListener("click", ".pl_close_app_drawer", this._plHideFavIcons);
      useListener("click", ".o_app", this._onPlAppsMenuItemClicked);

      var today = new Date();
      var curHr = today.getHours();
      var message = "Hi, ";
      if (curHr < 12) {
        message = "Good Morning, ";
      } else if (curHr < 18) {
        message = "Good Afternoon, ";
      } else {
        message = "Good Evening, ";
      }
      this.props["pl_user_id"] = session.uid;
      this.props["pl_user_name"] = message + session.name;
      this._pl_fuzzysearchableMenus = _.reduce(
        this.menuService.getApps(),
        pl_GetReducedMenuData.bind(this),
        {}
      );
    },

    willStart: async function () {
      const _super = this._super.bind(this);
      var apps = this.menuService.getApps();
      var pl_fav_apps = false;
      var data = false;

      await ajax
        .jsonRpc("/pl_app_frequency/render", "call", {})
        .then(function (app_frequency) {
          data = app_frequency;
        });
      await ajax
        .jsonRpc("/pl_curved_theme/get_fav_icons", "call", {
          pl_app_icons: apps,
        })
        .then(function (data) {
          pl_fav_apps = data;
        });

      this.apps = pl_fav_apps;
      this.pl_fav_apps = pl_fav_apps;
      this.props["_pl_frequent_apps"] = [];

      data.forEach((item, index) => {
        var frequent_app = apps.filter((app) => {
          if (app.id == item) return app;
        });
        this.props._pl_frequent_apps.push(frequent_app[0]);
      });

      return _super(...arguments);
    },

    mounted: function () {
      this.$search_container = $(this.el).find(".pl_menu_search");
      this.$search_input = $(this.el).find(".pl_menu_search_box input");
      this.$search_results = $(this.el).find(".pl-search-values");
      return this._super.apply(this, arguments);
    },

    /**
     * To split the object into chunpl of 12
     * @returns {Object[]}
     */
    _getSplittedApps: function () {
      var apps = this.pl_fav_apps;
      var i,
        j,
        app_list = [],
        chunk = 12;
      for (i = 0, j = apps.length; i < j; i += chunk) {
        app_list.push(apps.slice(i, i + chunk));
      }
      return app_list;
    },

    /**
     * To get frequent apps of current user
     * @returns {Object[]}
     */
    _getFrequentApps: function () {
      return this.props["_pl_frequent_apps"];
    },

    _plHideFavIcons: function (ev) {
      ev.preventDefault();
      var self = this;
      document.body.classList.remove("pl_appsmenu_edit");

      $("div.pl_appdrawer_inner_app_div")
        .find("span.pl_fav_icon")
        .addClass("d-none");
      $("div.pl_appdrawer_div")
        .find("div.pl-app-drawer-close")
        .addClass("d-none");
    },

    //--------------------------------------------------------------------------
    // Searching
    //--------------------------------------------------------------------------
    // FixMe: Optimize the code and correct Naming (Copied)

    _plSearchFocus: function () {
      // ToDo: Only for mobile, check its usage
      if (!config.device.isMobile) {
        this.$search_input.focus();
      }
    },

    _plSearchMenuListTime: function () {
      this._pl_search_def = new Promise((resolve) => {
        setTimeout(resolve, 50);
      });
      this._pl_search_def.then(this._plSearchMenusList.bind(this));
    },

    _plSearchResetvalues: function () {
      this.$search_container.removeClass("pl-find-values");
      this.$search_results.empty();
      this.$search_input.val("");
    },

    _plSearchMenusList: function () {
      var query = this.$search_input.val();
      if (query === "") {
        this.$search_container.removeClass("pl-find-values");
        this.$search_results.empty();
        return;
      }
      query = query.toLowerCase();
      var _newdata_app = _.filter(
        this._pl_fuzzysearchableMenus,
        function (menu) {
          return (
            menu.pl_title && !menu.pl_parent_id && menu.pl_title.includes(query)
          );
        }
      );
      var _newdata_items = _.filter(
        this._pl_fuzzysearchableMenus,
        function (menu) {
          return (
            menu.pl_title && menu.pl_parent_id && menu.pl_title.includes(query)
          );
        }
      );
      this.$search_container.toggleClass(
        "pl-find-values",
        Boolean(_newdata_app.length + _newdata_items.length)
      );
      this.$search_results.html(
        QWeb.render("pl_curved_backend_theme.pl_search_menu_items", {
          pl_menu_items: _newdata_items,
          pl_menu_app: _newdata_app,
        })
      );
    },

    _plSearchValuesSelecter: function (ev) {
      document.body.classList.toggle("pl_appsmenu_active");
      if (document.body.classList.contains("pl_appsmenu_active")) {
        document.body.classList.remove("brightness");
        this.trigger("pl_manage_drawer", {
          drawer_status: "open",
        });
      } else {
        document.body.classList.add("brightness");
        this.trigger("pl_manage_drawer", {
          drawer_status: "close",
        });
      }
      //      }, 2000);
    },

    _plSearchValuesMovement: function (ev) {
      var all = this.$search_results.find(".pl-menu-search-value"),
        pre_focused = all.filter(".active") || $(all[0]);
      var offset = all.index(pre_focused),
        key = ev.key;
      if (!all.length) {
        return;
      }
      if (key === "Tab") {
        ev.preventDefault();
        key = ev.shiftKey ? "ArrowUp" : "ArrowDown";
      }
      switch (key) {
        case "Enter":
          pre_focused.click();
          break;
        case "ArrowUp":
          offset--;
          break;
        case "ArrowDown":
          offset++;
          break;
        default:
          return;
      }
      if (offset < 0) {
        offset = all.length + offset;
      } else if (offset >= all.length) {
        offset -= all.length;
      }

      const new_focused = $(all[offset]);
      pre_focused.removeClass("active");
      new_focused.addClass("active");
      this.$search_results.scrollTo(new_focused, {
        offset: {
          top: this.$search_results.height() * -0.5,
        },
      });
    },

    _plHideAppsMenuList: function (ev) {
      return !this.$("input").is(":focus");
    },

    _plManageFavApps: function (ev) {
      if ($(ev.currentTarget).hasClass("pl_add_fav")) this._plAddFavApps(ev);
      else this._plRemoveFavApps(ev);
    },

    _plAddFavApps: async function (ev) {
      ev.preventDefault();
      var pl_current_target = $(ev.currentTarget);
      let result = await this.env.services.rpc(
        "/pl_curved_theme/set_fav_icons",
        {
          pl_app_id:
            ev.currentTarget.previousElementSibling.getAttribute(
              "data-menu-id"
            ),
        }
      );
      if (result) {
        // this.trigger("pl_update_fav_icon");
        this.pl_update_fav_icon();
        this._plRemFromFav(ev, pl_current_target);
      }
    },

    _plRemoveFavApps: async function (ev) {
      ev.preventDefault();
      var pl_current_target = $(ev.currentTarget);
      const result = await this.env.services.rpc(
        "/pl_curved_theme/rmv_fav_icons",
        {
          pl_app_id:
            ev.currentTarget.previousElementSibling.getAttribute(
              "data-menu-id"
            ),
        }
      );
      if (result) {
        // this.trigger("pl_update_fav_icon");
        this.pl_update_fav_icon();
        this._plAddToFav(ev, pl_current_target);
      }
    },

    pl_update_fav_icon: function () {
      this._appsBar = new plAppSidebar(this, this.menuService.getApps());
      this.$menu_apps_sidebar = $(".pl_left_sidebar_panel").find(
        ".inner-sidebar"
      );
      $("div.pl_favt_apps").remove();
      this._appsBar.prependTo(this.$menu_apps_sidebar);
    },

    _plAddToFav: function (ev, pl_current_target) {
      // Change Class.
      $(pl_current_target).removeClass("pl_rmv_fav");
      $(pl_current_target).addClass("pl_add_fav");

      // Change icon
      $(pl_current_target)
        .find("img")
        .attr("src", "pl_curved_backend_theme/static/src/images/star.svg");

      // Deactive app
      // $(ev.currentTarget.parentElement).removeClass('pl_add_visible');
    },

    _plRemFromFav: function (ev, pl_current_target) {
      // Change Class.
      $(pl_current_target).removeClass("pl_add_fav");
      $(pl_current_target).addClass("pl_rmv_fav");

      // Change icon
      $(pl_current_target)
        .find("img")
        .attr("src", "pl_curved_backend_theme/static/src/images/fav_ic.svg");

    },

      /**
     * Open the first app in the list of apps
     */


    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Called when clicking on an item in the apps menu
     * To hide the App drawer on clicking apps
     * @override
     * @param {MouseEvent} ev
     */
    _onPlAppsMenuItemClicked: function (ev) {
      document.body.classList.toggle("pl_appsmenu_active");
      if (document.body.classList.contains("pl_appsmenu_active")) {
        document.body.classList.remove("brightness");
        this.trigger("pl_manage_drawer", {
          drawer_status: "open",
        });
      } else {
        document.body.classList.add("brightness");
        this.trigger("pl_manage_drawer", {
          drawer_status: "close",
        });
      }
    },
    //
    //        /**
    //         * @private
    //         * @param {Object} app
    //         */
    //        _setActiveApp: function(app) {
    //            var $oldActiveApp = this.$(".o_app.active");
    //            $oldActiveApp.removeClass("active");
    //            var $newActiveApp = this.$(
    //                '.o_app[data-action-id="' + app.actionID + '"]'
    //            );
    //            //Do not set active on frequent apps menu
    //            //$newActiveApp.addClass('active');
    //        },

    /**
     * @override this method to update the app frequency counter.
     */
    render: function(){
      this._super();
      if (this.menuService.getCurrentApp()){
        let pl_update_app = ajax
          .jsonRpc("/pl_app_frequency/update", "call", {
            menu_id: this.menuService.getCurrentApp().id,
          });
      }
    }
  });
});
