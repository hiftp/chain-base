odoo.define("pl_curved_backend_theme.pl_bookmarpl", function (require) {
  "use strict";

  var Widget = require("web.Widget");
  var ajax = require("web.ajax");
  var core = require("web.core");
  var _t = core._t;

  var qweb = core.qweb;

  var PlBookmarpl = Widget.extend({
    template: "pl_curved_backend_theme.bookmark_bar",
    events: _.extend({}, Widget.prototype.events, {
      "click .pl-bookmarpl-menu-toggle": "_plBookmarplToggle",
      "click .pl-save-bookmark": "_plSaveBookmark",
      "show.bs.dropdown .pl_add_bookmark_dropdown": "_plAddBookmark",
      "click #addBookmarkDropdown": "_plAddBookmarkDiv",
      "click .pl-btn-inn": "_plSizeInc",
      "click .pl-btn-dec": "_plSizeDec",
      "click .pl-btn-reset": "_plSizeReset",
      "click .pl-btn-zoom": "_plZoomButton",
      "contextmenu .bookmark-link": "_plRightClick",
    }),

    init: function () {
      var self = this;
      document.bookmark_id;
      document.bookmark_name;
      document.bookmark_position;
      this._super.apply(this, arguments);
    },

    start: function () {
      var self = this;
      ajax.jsonRpc("/render/bookmarpl", "call", {}).then(function (data) {
        $(".pl-bookmark-panel").append(data);
      });
      $("body").append(
        '<div class="pl-bookmark-dropdown">' +
          '<div class="pl-bookmark-dropdown-content">' +
          '<div id="pl-bookmark-rename" class="pl-bookmark-option">Rename</div>' +
          '<div id="pl-bookmark-delete" class="pl-bookmark-option">Delete</div>' +
          '<div id="pl-bookmark-moveup" class="pl-bookmark-option">Move-Up</div>' +
          '<div id="pl-bookmark-movedown" class="pl-bookmark-option">Move-Down</div>' +
          "</div>" +
          "</div>"
      );

      $("body").append(
        '<div id="renameBookmarkDropdown" class="pl-rename-bookmark-dropdown">' +
          '<div class="pl-rename-bookmark-header pt-2 px-3">Rename</div>' +
          '<div class="pl-rename-bookmark-body py-2 px-3">' +
          '<div class="form-group m-0">' +
          '<input type="text" class="form-control" placeholder="Name" id="pl_rename_bookmark"/>' +
          "</div>" +
          "</div>" +
          '<div class="pl-rename-bookmark-footer py-2 px-3">' +
          '<button type="button" class="btn btn-primary pl-rename-bookmark">Rename</button>' +
          '<button type="button" class="btn btn-default pl-rename-cancel">Cancel</button>' +
          "</div>" +
          "</div>"
      );
      document
        .getElementById("pl-bookmark-rename")
        .addEventListener("click", self._plBookmarkRename);
      document
        .getElementById("pl-bookmark-delete")
        .addEventListener("click", self._plBookmarkDelete);
      document
        .getElementById("pl-bookmark-moveup")
        .addEventListener("click", self._plBookmarkMoveup);
      document
        .getElementById("pl-bookmark-movedown")
        .addEventListener("click", self._plBookmarkMovedown);
    },

    // Displayed using bootstrap
    _plAddBookmark: function (ev) {
        $("#bookmark_name").val("");
        $.each($('.breadcrumb-item'), function() {
            if($(this).text().length){
                if($("#bookmark_name").val().length)
                    var val = $("#bookmark_name").val() + '/' + $(this).text();
                else
                    var val = $(this).text();
                $("#bookmark_name").val(val);
            }
        });
    },
    // To prevent closing of div
    _plAddBookmarkDiv: function (ev) {
      if (!ev.target.classList.contains("btn")) {
        ev.stopPropagation();
        ev.preventDefault();
        $("#pl_bookmark_alert").hide("slow");
      }
    },

    _plSaveBookmark: function (ev) {
      if ($("#bookmark_name").val() == false) {
        ev.stopPropagation();
        ev.preventDefault();
        $("#pl_bookmark_alert").show("slow");
      } else {
        var bookmark_name = $("#bookmark_name").val();
        var bookmark_url =
          "/web#" + location.href.replace(/^[^#]*#?(.*)$/, "$1");
        var bookmark_position = $(".bookmark-item").length + 1;
        $("#addBookmarkDropdown").toggleClass("show");
        ajax
          .jsonRpc("/update/bookmarpl", "call", {
            create_new: "create_new",
            bookmark_name: bookmark_name,
            bookmark_url: bookmark_url,
            bookmark_position: bookmark_position,
          })
          .then(function (data) {
            $(".pl-bookmark-panel").html(data);
            $(".pl_add_bookmark_dropdown").dropdown("dispose");
          });
        $("#pl_bookmark_alert").hide("slow");
      }
    },

    _plBookmarplToggle: function () {
      document.body.classList.toggle("pl_show_bookmark");
    },

    _plRightClick: function (event) {
      document.bookmark_id = event.currentTarget.getAttribute("data-id");
      document.bookmark_position =
        event.currentTarget.getAttribute("data-position");
      document.bookmark_name = event.currentTarget.getAttribute("data-name");
      $("#pl-bookmark-movedown").removeClass("d-none");
      $("#pl-bookmark-moveup").removeClass("d-none");
      if (document.bookmark_position == $(".bookmark-item").length) {
        $("#pl-bookmark-movedown").addClass("d-none");
      }
      if (document.bookmark_position == "1") {
        $("#pl-bookmark-moveup").addClass("d-none");
      }
      $(".pl-bookmark-dropdown").css({
        left: event.pageX - $(".pl-bookmark-dropdown").width(),
        top: event.pageY,
        display: "block",
      });
      window.addEventListener("click", () => {
        $(".pl-bookmark-dropdown").hide();
      });
      event.preventDefault();
    },

    // --- Zoom Functionality --- //
    plResize: function (scale_value) {
      document.querySelector(".pl-zoom-per").innerText =
        String(scale_value) + "%";

      if (document.querySelector(".o_content").children.length == 1){
        var o_content_style = document.querySelector(
            ".o_content div:last-child"
          ).style;
      }
      else{
        var o_content_style = document.querySelector(
            ".o_content"
          ).style;
      }

      o_content_style.transform = "scale(" + scale_value / 100 + ")";
      o_content_style.transformOrigin = "left top";
      if ($('body.o_rtl').length)
        o_content_style.transformOrigin = "right top";
      o_content_style.width = 100 * (100 / scale_value) + "%";
      o_content_style.flex = "0 0 " + 100 * (100 / scale_value) + "%";
    },
    // Displayed using bootstrap
    _plZoomButton: function (ev) {
      window.addEventListener("click", () => {
        $("#zoomPanel").removeClass("show");
      });
    },
    _plSizeInc: function (ev) {
      ev.stopPropagation();
      if ($(".o_content").length) {
        var scale_value =
          parseInt(
            document.querySelector(".pl-zoom-per").innerText.replace("%", "")
          ) + 10;
        this.plResize(scale_value);
        $(".pl-btn-dec")[0].removeAttribute("disabled");
        if (scale_value >= 500) {
          ev.currentTarget.setAttribute("disabled", true);
        }
      }
    },
    _plSizeDec: function (ev) {
      ev.stopPropagation();
      if ($(".o_content").length) {
        var scale_value =
          parseInt(
            document.querySelector(".pl-zoom-per").innerText.replace("%", "")
          ) - 10;
        this.plResize(scale_value);
        $(".pl-btn-inn")[0].removeAttribute("disabled");
        if (scale_value <= 20) {
          ev.currentTarget.setAttribute("disabled", true);
        }
      }
    },
    _plSizeReset: function (ev) {
      ev.stopPropagation();
      if ($(".o_content").length) {
        if(document.querySelector(".o_content").children.length == 1){
            document
          .querySelector(".o_content div:last-child")
          .removeAttribute("style");
        }
        else{
            document
          .querySelector(".o_content")
          .removeAttribute("style");
        }

        document.querySelector(".pl-zoom-per").innerText = "100%";
      }
    },

    // --- Bookmark --- //
    _plBookmarkRename: function () {
      $("#pl_rename_bookmark").val(document.bookmark_name);
      $(".pl-rename-bookmark-dropdown").css({
        left: event.pageX - $(".pl-rename-bookmark-dropdown").width(),
        top: event.pageY,
        display: "block",
      });
      $(".pl-rename-cancel")[0].addEventListener("click", () => {
        $(".pl-rename-bookmark-dropdown")[0].style.display = "none";
      });

      $(".pl-rename-bookmark")[0].addEventListener("click", () => {
        var name = $("#pl_rename_bookmark").val();
        var id = document.bookmark_id;
        if (name == false) {
          this.call("notification", "notify", {
            title: _t("Can't be Empty"),
            message: _t("Please enter the Name of Bookmark."),
            sticky: false,
          });
        } else {
          $(".pl-rename-bookmark-dropdown")[0].style.display = "none";
          ajax
            .jsonRpc("/update/bookmarpl", "call", {
              bookmark_name: name,
              rename: "rename",
              bookmark_id: id,
            })
            .then(function (data) {
              $(".pl-bookmark-panel").html(data);
            });
        }
      });
      event.preventDefault();
    },
    _plBookmarkDelete: function () {
      var id = document.bookmark_id;
      ajax
        .jsonRpc("/update/bookmarpl", "call", {
          delete: "delete",
          bookmark_id: id,
        })
        .then(function (data) {
          $(".pl-bookmark-panel").html(data);
        });
    },
    _plBookmarkMoveup: function () {
      var id = document.bookmark_id;
      ajax
        .jsonRpc("/update/bookmarpl", "call", {
          reposition: "move_up",
          bookmark_position: document.bookmark_position,
          bookmark_id: document.bookmark_id,
        })
        .then(function (data) {
          $(".pl-bookmark-panel").html(data);
        });
    },
    _plBookmarkMovedown: function () {
      ajax
        .jsonRpc("/update/bookmarpl", "call", {
          reposition: "move_down",
          bookmark_position: document.bookmark_position,
          bookmark_id: document.bookmark_id,
        })
        .then(function (data) {
          $(".pl-bookmark-panel").html(data);
        });
    },
  });
  return PlBookmarpl;
});
