odoo.define(
  "pl_curved_backend_theme.pl_left_sidebar_panel",
  function (require) {
    "use strict";

    var config = require("web.config");
    // To check the device

    var { NavBar } = require("@web/webclient/navbar/navbar");
    var SystrayMenu = require("web.SystrayMenu");
    var dom = require("web.dom");
    var session = require("web.session");
    var UserMenu = require("@web/webclient/user_menu/user_menu");
//import { menuService } from "@web/webclient/menus/menu_service";
//    var { MenusService } = require("@web/webclient/menus/menu_service");
    var plAppSidebar = require("pl_curved_backend_theme.pl_app_sidebar");
    var plBookmarpl = require("pl_curved_backend_theme.pl_bookmarpl");
    var core = require("web.core");
    var QWeb = core.qweb;
    var { patch } = require("web.utils");
    const { useListener } = require("web.custom_hoopl");
    var ajax = require("web.ajax");

    const { hoopl } = owl;
    const { onWillStart } = hoopl;
    // Handle rpc calls.
    var { useService } = require("@web/core/utils/hoopl");

    // todo: Patch the remaining methods from the below commented code
    patch(NavBar.prototype, "pl_left_sidebar_panel", {
      async setup(parent, menuData) {
        this._super();
        this.parent = parent;
        this._apps = menuData;
        this.rpc = useService("rpc");
        useListener("click", "#pl_app_drawer_toggle", this._plAppsDrawerClick);
        useListener("click", "button.phone-menu-btn", this._plOpenMobileDrawer);
        useListener("click", "a[data-section]", this._plSubMenu);
        useListener("pl_manage_drawer", this._plManagerDrawer);
        useListener( "click", "div.overlay", this._plCloseMobileDrawer);
        useListener( "click", ".pl_menusections li .dropdown-menu a", this._plCloseMobileDrawer);
        useListener( "click", ".pl_menusections li a[data-action-id]", this._plCloseMobileDrawer);
        useListener( "DOMMouseScroll", ".pl_appdrawer_div", this._onPageScroll); // Firefox
        useListener( "mousewheel", ".pl_appdrawer_div", this._onPageScroll); // Chrome, Safari, IE
        this._plBookmarpl();

      },

      async willStart() {
        let self = this;
        const _super = this._super.bind(this, ...arguments);
        let pl_data = await ajax.jsonRpc("/web/dataset/call", "call", {
          model: "pl.global.config",
          method: "pl_get_value_from_scope",
          args: [
            [
              "pl_menu_bar",
              "pl_favorite_bar",
              "pl_company_logo",
              "pl_favtbar_autohide",
              "pl_favtbar_position",
              "pl_show_app_name",
              "pl_user_menu_placement",
              "pl_menubar_autohide",
              "pl_small_company_logo",
            ],
          ],
        });

        // Add menu bar info.
        this.init_menu_data(pl_data);

        if (this.pl_menu_bar == "Vertical")
          document.body.classList.add("pl_vertical_body_panel");

        if (
          self.pl_favtbar_autohide &&
          self.pl_favorite_bar &&
          self.pl_menu_bar == "Horizontal"
        )
          document.body.classList.add("pl_favtbar_autohide");

        if (self.pl_menubar_autohide && screen.width > 1024)
          document.body.classList.add("pl_menubar_autohide");
        if (
          self.pl_favtbar_position == "Bottom" &&
          self.pl_menu_bar == "Horizontal"
        )
          document.body.classList.add("pl_favtbar_bottom");

//        if (
//          self.pl_user_menu_placement == "Top" &&
//          self.pl_menu_bar == "Vertical"
//        )
//        {
//          document.body.classList.add("pl_user_menu_top");
//          let child = document.querySelector(".o_user_menu");
//            let parent = document.querySelector(".inner-sidebar");
//
//            parent.appendChild(child);
//        }
        if (!self.pl_show_app_name && self.pl_favorite_bar)
          document.body.classList.add("pl_hide_app_names");

        if (self.pl_menu_bar == "Horizontal" && !self.pl_favorite_bar)
          document.body.classList.add("pl_hide_leftpanel");

        return _super();
      },

      // mounted() {
      willPatch() {
        var self = this;
        this.$menu_apps = $(".o_menu_apps");
        var base_url = session['web.base.url'];
        var logout_url='<a href='+ base_url+"/web/session/logout "+ 'class="dropdown-item focus" data-menu="logout">Log out</a>'

        if (this.pl_menu_bar == "Horizontal") {
          this.$menu_brand_placeholder = $(".o_menu_brand");
          this.$section_placeholder = $(".o_menu_sections");

          // Remove my-profile and logout buttons for horizontal menu bar on mobile.
          var pl_my_profile = $(".pl_user_action_horizontal").find('a[data-menu="settings"]').remove();
          var pl_logout = $(".pl_user_action_horizontal").find('a[data-menu="logout"]').remove();

          // Add buttons on mobile left navigation.
          $("div.pl-phone-profile").after('<div class="pl_mobile_nav_bottom">'+logout_url+'</div>');
//          $("div.pl_mobile_nav_bottom").append(pl_my_profile);
//          $("div.pl_mobile_nav_bottom").append(pl_logout);
//          $("nav.o_main_navbar .pl-phone-side-menu").on("click",".pl-phone-menu-list .pl_mobile_nav_bottom a[data-menu]",
//            function (ev) {
//              ev.preventDefault();
//              var menu = $(this).data("menu");
//              self.plMobileUserMenu[
//                "_onMenu" + menu.charAt(0).toUpperCase() + menu.slice(1)
//              ]();
//              self._plCloseMobileDrawer();
//            }
//          );
        }
        else if (this.pl_menu_bar == "Vertical") {

          if (self.pl_user_menu_placement == "Top")
            {
              document.body.classList.add("pl_user_menu_top");
              let user_button = document.querySelector(".o_user_menu");
              let inner_sidebar = document.querySelector(".inner-sidebar");
              inner_sidebar.appendChild(user_button);
            }

//        let child = document.querySelector(".o_user_menu");
//        let parent = document.querySelector(".inner-sidebar");
//
//        parent.appendChild(child);

          this.$menu_brand_placeholder =
            $(".pl_vertical_menus").find(".o_menu_brand");

          this.$section_placeholder =
            $(".pl_vertical_menus").find(".o_menu_sections");

          this.$menu_icon = $(".pl_vertical_menus").find(
            ".pl_vertical_app_icon"
          );

          // Side bar app menu for vertical menubar.
          if (this.currentApp && this.currentApp.webIconData) {
            this.$menu_icon.attr({
              alt: this.currentApp.name,
              title: this.currentApp.name,
              src: "data:image/png;base64," + this.currentApp.webIconData,
            });

            $(".pl_menubrand").text(this.currentApp.name);
            $(".pl_menubrand").attr('href', '#menu_id='+this.currentApp.appID);
          }

          // Vertical app menu drawer open.
//          $("div.pl_left_sidebar_panel .pl_app_sidebar .inner-sidebar").on("click","button.phone-menu-btn",
//            self._plOpenMobileDrawer.bind(self)
//          );

          // Vertical app menu drawer close.
//          $("div.pl_left_sidebar_panel .pl_app_sidebar .inner-sidebar").on("click","div.overlay",
//            self._plCloseMobileDrawer.bind(self)
//          );

          // Vertical menu binding
//          $("div.pl_left_sidebar_panel .pl_app_sidebar .inner-sidebar").on("click", "a[data-menu]", self._plMobileDrawerMenu.bind(self));

          // Vertical user data append and binding.
          // var pl_user_action = QWeb.render("UserMenu.Actions");
          // $("div.pl_user_action").html(pl_user_action);

          // Remove my-profile and logout buttons for vertical menu bar on mobile.
          var pl_my_profile = $(".pl_user_action").find('a[data-menu="settings"]').remove();
          var pl_logout = $(".pl_user_action").find('a[data-menu="logout"]').remove();

          // Add buttons on mobile left navigation.
          $("div.pl-phone-profile").after('<div class="pl_mobile_nav_bottom">'+logout_url+'</div>');
//          $("div.pl_mobile_nav_bottom").append(pl_my_profile);
//          $("div.pl_mobile_nav_bottom").append(pl_logout);

          // Handle menu of user action
//          $("div.pl_left_sidebar_panel .pl_app_sidebar .inner-sidebar").on("click",".pl-phone-menu-list .pl-phone-profile a[data-menu]",
//            function (ev) {
//              ev.preventDefault();
//              var menu = $(this).data("menu");
//              self.plMobileUserMenu[
//                "_onMenu" + menu.charAt(0).toUpperCase() + menu.slice(1)
//              ]();
//              self._plCloseMobileDrawer();
//            }
//          );

          // Handle my profile and logout button
//          $("div.pl_left_sidebar_panel .pl_app_sidebar .inner-sidebar").on("click",".pl-phone-menu-list .pl_mobile_nav_bottom a[data-menu]",
//            function (ev) {
//              ev.preventDefault();
//              var menu = $(this).data("menu");
//              self.plMobileUserMenu[
//                "_onMenu" + menu.charAt(0).toUpperCase() + menu.slice(1)
//              ]();
//              self._plCloseMobileDrawer();
//            }
//          );

        }


        this.$right_sidebar = $(".pl_right_sidebar_panel");

        // Navbar's menus event handlers
//        var on_secondary_menu_click = function (ev) {
//          ev.preventDefault();
//          var menu_id = $(ev.currentTarget).data("menu");
//          var action_id = $(ev.currentTarget).data("action-id");
//           self._on_secondary_menu_click(menu_id, action_id);
//        };
//        var menu_ids = _.keys(this.currentAppSections);
//        var primary_menu_id, $section, secon_menu;
//        for (var i = 0; i < menu_ids.length; i++) {
//          primary_menu_id = menu_ids[i];
//          $section = this.currentAppSections[primary_menu_id]["childrenTree"];
//          for (var i = 0; i < $section.length; i++) {
//            secon_menu = $section[i];
//            $(".dropdown-item").text(secon_menu.name);
//            $(".dropdown-item").attr('href', '#menu_id='+secon_menu.appID & secon_menu.actionID);
//          }
//          $section.on(
//            "click",
//            "a[data-menu]",
//            self,
//            on_secondary_menu_click.bind(this)
//            );
//          }

        this._plUpdateFavIcon();
        this.fav_app_rendered = true;
      // Apps Menu
        let tabContent = document.querySelectorAll(".tabContent .item");
        let plTabs = document.querySelectorAll(".pl-tabs li");
        plTabs.forEach((el, i) => {
          el.addEventListener("click", () => {
            plTabs.forEach((rm) => {
              rm.classList.remove("active");
            });
            el.classList.add("active");
            tabContent.forEach((tabCont) => {
              tabCont.classList.remove("active");
            });
            tabContent[i].classList.add("active");
          });
        });

      },

      _plOpenMobileDrawer: function () {
        // Append user's info
            var pl_user_name = session['name'];
            var pl_user_img_src = $('.o_menu_systray div.o_user_menu img')[0].src;
            if (pl_user_name) {
              $("div.pl-phone-profile .pl_user_name").text(pl_user_name);
            }
            if (pl_user_img_src) {
              $("div.pl-phone-profile .pl-user-profile-img img").attr(
                "src",
                pl_user_img_src
              );
            }

            if ($("div.pl-phone-side-menu").length){
              $("div.pl-phone-side-menu").addClass("active-menu");
              if((this.pl_menu_bar=='Vertical') &&($("ul.pl_menusections").length))
                $("div.pl-phone-profile").after($("ul.pl_menusections")[0].outerHTML);
              setTimeout(() => {
                $("div.pl-phone-menu-list").addClass("menu-show");
              }, 200);
            }
      },

      _plCloseMobileDrawer: function () {
        if ($("div.pl-phone-menu-list").hasClass("menu-show")) {
          $("div.pl-phone-menu-list").removeClass("menu-show");
        if(this.pl_menu_bar=='Vertical')
          $("div.pl-phone-menu-list").find("ul.o_menu_sections").remove();
          setTimeout(() => {
            $("div.pl-phone-side-menu").removeClass("active-menu");
          }, 200);
        }
      },

      _plUpdateFavIcon: function () {
        if (this.currentApp && !this.fav_app_rendered) {
          this._appsBar = new plAppSidebar(
            this,
            this.menuService.getApps()
          );
          this.$menu_apps_sidebar = $(".pl_left_sidebar_panel").find(
            ".inner-sidebar"
          );
          $("div.pl_favt_apps").remove();
          this._appsBar.prependTo(this.$menu_apps_sidebar);
        }
        // Remove active app from left side bar.
        // Active app if app is present in the favorite bar.
        if (this._appsBar && this.menuService)
          this._appsBar._setActiveApp(this.menuService.getCurrentApp());
      },

      init_menu_data(pl_data) {
        this.pl_menu_bar = pl_data.pl_menu_bar;
        this.pl_favorite_bar = pl_data.pl_favorite_bar;
        this.pl_favtbar_autohide = pl_data.pl_favtbar_autohide;
        this.pl_menubar_autohide = pl_data.pl_menubar_autohide;
        this.pl_favtbar_position = pl_data.pl_favtbar_position;
        this.pl_company_logo = pl_data.pl_company_logo;
        this.pl_show_app_name = pl_data.pl_show_app_name;
        this.pl_user_menu_placement = pl_data.pl_user_menu_placement;
        this.pl_small_company_logo = pl_data.pl_small_company_logo;
      },

      _plBookmarpl() {
        this.$right_sidebar = $(".pl_right_sidebar_panel");
        this._bookmark_bar = new plBookmarpl();
        this._bookmark_bar.appendTo(this.$right_sidebar);
      },


      _plSubMenu(event) {
        var dataset = event.path[0]
          this.menuService.selectMenu(Number(dataset.dataset.section));
                },

      _onPageScroll: function (event) {
        if (event.target.closest('#AllApps')){
            return true;
        }
        event.preventDefault();
        // scroll down
        if (event.deltaY > 0 && event.deltaY < 110 && $('#AllApps').hasClass('active')){
           if ($('.pl-tabs li.active').next().length > 0){
              var li = $('.pl-tabs li.active').next();
              $('.pl-tabs li.active').removeClass("active");
              li.addClass("active");
              var ui = $("#AllApps > div.active");
              var mi = $("#AllApps > div.active").next();
              ui.removeClass("active");
              mi.addClass("active");
           }
        }
        // scroll up
        else if (event.deltaY < 0 && event.deltaY > -110 && $('#AllApps').hasClass('active')){
           if ($('.pl-tabs li.active').prev().length > 0){
              var li = $('.pl-tabs li.active').prev();
              $('.pl-tabs li.active').removeClass("active");
              li.addClass("active");
              var ui = $("#AllApps > div.active");
              var mi = $("#AllApps > div.active").prev();
              ui.removeClass("active");
              mi.addClass("active");
           }
        }
      },

      /**
       * Show & hide app drawer
       *
       * @private
       * @param {MouseEvent} event
       */
      _plAppsDrawerClick(event) {
        // To prevent opening default app
        event.stopPropagation();
        event.preventDefault();
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
        var owl = $(".owl-carousel");
        owl.owlCarousel({
          ltr: true,
          dots: true,
          dotsEach: true,
          items: 1,
          animateIn: "fadeIn",
        });
      },

      _plManagerDrawer(drawer_status) {
        $('#pl_input_text').focus();
        this.$search_container.removeClass("pl-find-values");
        this.$search_results.empty();
        this.$search_input.val("");
        if (drawer_status.detail && drawer_status.detail.drawer_status) {
          if (drawer_status.detail.drawer_status == "open") {
            if ($("html").attr("data-drawer-font-style") == "dark")
              $("html").attr("data-color-mode", "pl-dark");
            else if ($("html").attr("data-drawer-font-style") == "light")
              $("html").attr("data-color-mode", "pl-light");

            // Manage App drawer theme color.
            document.body.style.removeProperty("--body-background");
            document.body.style.removeProperty("--nav-link-color");
            document.body.style.removeProperty("--pl-over-link");
            $("div.o_menu_systray").removeClass("pl_color_theme_dark_header");
            $(".o_main_navbar button.phone-menu-btn").removeClass(
              "pl_color_theme_dark_header"
            );
            $(
              ".pl_left_sidebar_panel .pl_app_sidebar .inner-sidebar button.phone-menu-btn"
            ).removeClass("pl_color_theme_dark_header");
          }
          if (drawer_status.detail.drawer_status == "close") {
            $("html").attr("data-color-mode", session.pl_current_color_mode);

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
              $(".o_main_navbar button.phone-menu-btn").addClass(
                "pl_color_theme_dark_header"
              );
              $(
                ".pl_left_sidebar_panel .pl_app_sidebar .inner-sidebar button.phone-menu-btn"
              ).addClass("pl_color_theme_dark_header");
            }
          }
        }
      },

      //@Todo: Check this function
      change_menu_section: function (primary_menu_id) {
        if (primary_menu_id && this.pl_favorite_bar)
          this._appsBar._setActiveApp(primary_menu_id);
        this._super.apply(this, arguments);
        if (primary_menu_id && this.pl_menu_bar == "Vertical") {
          var active_menu = this.menu_data.children.find(
            (x) => x.id === primary_menu_id
          );
          var $menu_icon = this.$menu_icon;
          if (active_menu) {
            $menu_icon.attr({
              alt: active_menu.name,
              title: active_menu.name,
              src: "data:image/png;base64," + active_menu.web_icon_data,
            });
          }
        }
        // For Frequency of Apps 👇
        if (primary_menu_id) {
          this._rpc({
            route: "/pl_app_frequency/update",
            params: {
              menu_id: primary_menu_id,
            },
          });
        }

      },

//      _plMobileDrawerMenu: function (ev) {
//        var self = this;
//        ev.preventDefault();
//        var menu_id = $(ev.currentTarget).data("menu");
//        var action_id = $(ev.currentTarget).data("action-id");
//        self._on_secondary_menu_click(menu_id, action_id);
//        self._plCloseMobileDrawer();
//      },
    });
});
