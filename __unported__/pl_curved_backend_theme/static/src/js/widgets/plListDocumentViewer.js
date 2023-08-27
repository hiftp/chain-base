odoo.define("pl_curved_backend_theme.PlListDocumentViewer", function (require) {
  "use strict";

  var core = require("web.core");
  var Widget = require("web.Widget");

  var QWeb = core.qweb;

  var PlListDocumentViewer = Widget.extend({
    template: "pl_curved_backend_theme.PlListDocumentViewer",
    events: {
      "click .o_viewer_img": "plOnImageClicked",
      "click .o_download_btn": "plOnDownload",
      "click .o_viewer_video": "plOnVideoController",
      "click .o_zoom_reset": "plPreviewZoomReset",
      "click .o_rotate": "plRotatePreview",
      "click .o_zoom_in": "plPreviewZoomIn",
      "click .o_zoom_out": "_plZoomOutPreview",
      "click .o_close_btn": "destroy",
      "click .o_print_btn": "_plOnPrintPreview",
      "DOMMouseScroll .o_viewer_content": "plOnScrollPreview", // Scroll for Firefox browser.
      "mousewheel .o_viewer_content": "plOnScrollPreview", // Scroll for Chrome, Safari, IE browser.
      keyup: "plOnKeyUp",
    },

    /**
     * Initialize list document viewer.
     */
    init: function (parent, pl_attachments, pl_activeAttachmentID) {
      this._super.apply(this, arguments);
      this.pl_attachment = _.filter(pl_attachments, function (pl_attachment) {
        if (pl_attachment.type === "url")
          var pl_match = pl_attachment.url.match("(.png|.gif|youtu|.jpg)");
        else
          var pl_match = pl_attachment.mimetype.match(
            "(image|video|text|application/pdf)"
          );

        if (pl_match) {
          pl_attachment.fileType = pl_match[1];
          if (pl_match[1] === "youtu") {
            var pl_youtube_arr = pl_attachment.url.split("/");
            var youtube_token = pl_youtube_arr[pl_youtube_arr.length - 1];
            if (youtube_token.indexOf("watch") !== -1) {
              youtube_token = youtube_token.split("v=")[1];
              var amp = youtube_token.indexOf("&");
              if (amp !== -1) {
                youtube_token = youtube_token.substring(0, amp);
              }
            }
            pl_attachment.youtube = youtube_token;
          }
          if (pl_match[1].match("(.jpg|.png|.gif)")) {
            pl_attachment.fileType = "image";
          }
          return true;
        }
      });
      this.pl_activeAttachment = _.findWhere(pl_attachments, {
        id: pl_activeAttachmentID,
      });
      this.modelName = "ir.attachment";
      this.plPreviewReset();
    },

    start: function () {
      this.$el.modal("show");
      this.$el.on("hidden.bs.modal", _.bind(this.plOnDestroy, this));
      this.$(".o_viewer_img").on("load", _.bind(this.plOnImageLoaded, this));
      this.$('[data-toggle="tooltip"]').tooltip({ delay: 0 });
      return this._super.apply(this, arguments);
    },

    destroy: function () {
      // Hide and remove modal.
      this.$el.modal("hide");
      this.$el.remove();
      // If preview is already destroyed.
      if (this.isDestroyed()) {
        return;
      }
      this._super.apply(this, arguments);
    },

    plPreviewReset: function () {
      this.scale = 1;
      this.dragStartX = this.dragstopX = 0;
      this.dragStartY = this.dragstopY = 0;
    },

    plPreviewGetTransform: function (scale, angle) {
      return (
        "scale3d(" + scale + ", " + scale + ", 1) rotate(" + angle + "deg)"
      );
    },

    plPreviewRotate: function (angle) {
      this.plPreviewReset();
      var new_angle = (this.angle || 0) + angle;
      this.$(".o_viewer_img").css(
        "transform",
        this.plPreviewGetTransform(this.scale, new_angle)
      );
      this.$(".o_viewer_img").css(
        "max-width",
        new_angle % 180 !== 0 ? $(document).height() : "100%"
      );
      this.$(".o_viewer_img").css(
        "max-height",
        new_angle % 180 !== 0 ? $(document).width() : "100%"
      );
      this.angle = new_angle;
    },

    plPreviewZoom: function (scale) {
      if (scale > 0.5) {
        this.$(".o_viewer_img").css(
          "transform",
          this.plPreviewGetTransform(scale, this.angle || 0)
        );
        this.scale = scale;
      }
      this.$(".o_zoom_reset")
        .add(".o_zoom_out")
        .toggleClass("disabled", scale === 1);
    },

    plOnDestroy: function () {
      this.destroy();
    },

    /**
     * Handle download button.
     */
    plOnDownload: function (ev) {
      ev.preventDefault();
      window.location =
        "/web/content/" +
        this.modelName +
        "/" +
        this.pl_activeAttachment.id +
        "/" +
        "datas" +
        "?download=true";
    },

    /**
     * Handle print action.
     */
    _plOnPrintPreview: function (ev) {
      ev.preventDefault();
      var src = this.$(".o_viewer_img").prop("src");
      var script = QWeb.render("im_livechat.legacy.mail.PrintImage", {
        src: src,
      });
      var printWindow = window.open("about:blank", "_new");
      printWindow.document.open();
      printWindow.document.write(script);
      printWindow.document.close();
    },

    /**
     * Prevent image clicked.
     */
    plOnImageClicked: function (ev) {
      ev.stopPropagation();
    },

    /**
     * Hide loader when after the image load.
     */
    plOnImageLoaded: function () {
      this.$(".o_loading_img").hide();
    },

    /**
     * Handle mouse zoom.
     *
     */
    plOnScrollPreview: function (ev) {
      var scale;
      if (ev.originalEvent.wheelDelta > 0 || ev.originalEvent.detail < 0) {
        scale = this.scale + 0.1;
        this.plPreviewZoom(scale);
      } else {
        scale = this.scale - 0.1;
        this.plPreviewZoom(scale);
      }
    },

    /**
     * Control media video.
     */
    plOnVideoController: function (ev) {
      ev.stopPropagation();
      var plVideoElement = ev.target;
      if (plVideoElement.paused) {
        plVideoElement.play();
      } else {
        plVideoElement.pause();
      }
    },

    /**
     * Right rotate.
     */
    plRotatePreview: function (ev) {
      ev.preventDefault();
      this.plPreviewRotate(90);
    },

    /**
     * Reset preview content.
     */
    plPreviewZoomReset: function (ev) {
      ev.preventDefault();
      this.$(".o_viewer_zoomer").css("transform", "");
      this.plPreviewZoom(1);
    },

    /**
     * Handle zoom in functionality.
     */
    plPreviewZoomIn: function (ev) {
      ev.preventDefault();
      var plScale = this.scale + 0.5;
      this.plPreviewZoom(plScale);
    },

    /**
     * Handle zoom out functionality.
     */
    _plZoomOutPreview: function (ev) {
      ev.preventDefault();
      var plScale = this.scale - 0.5;
      this.plPreviewZoom(plScale);
    },

    plOnKeyUp: function (ev) {
      switch (ev.which) {
        case $.ui.keyCode.ESCAPE:
          ev.preventDefault();
          this.destroy();
          break;
      }
    },
  });

  return PlListDocumentViewer;
});
