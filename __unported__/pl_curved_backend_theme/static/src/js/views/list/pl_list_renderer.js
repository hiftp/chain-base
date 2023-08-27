odoo.define("pl_curved_backend_theme.pl_list_renderer", function (require) {
  "use strict";

  var ajax = require("web.ajax");
  var ListRenderer = require("web.ListRenderer");
  var PlListDocumentViewer = require("pl_curved_backend_theme.PlListDocumentViewer");
  var core = require("web.core");
  var _t = core._t;

  var Pl_ListRenderer = ListRenderer.include({
    events: _.extend({}, ListRenderer.prototype.events, {
      "click .pl_attachment_id": "_onplViewAttachment",
      "click tbody .pl_attachment_data": "_onplAttachmentDivClicked",
      "change input": "_onplInputChange",
    }),

    // Showing preview of attachments
    _onplViewAttachment: function (ev) {
      var att_id = parseInt($(ev.currentTarget).data("id"));
      var att_mime = $(ev.currentTarget).data("mime");
      var att_name = $(ev.currentTarget).data("name");
      var rec_id = parseInt($(ev.currentTarget).data("pl-rec-id"));
      var att_data = this.pl_data;

      var match = att_mime.match("(image|video|application/pdf|text)");
      if (match) {
        var pl_attachment = [];
        att_data[rec_id].forEach((attachment) => {
          if (attachment.att_mime.match("(image|video|application/pdf|text)")) {
            pl_attachment.push({
              filename: attachment.att_name,
              id: attachment.att_id,
              is_main: false,
              mimetype: attachment.att_mime,
              name: attachment.att_name,
              type: attachment.att_mime,
              url: "/web/content/" + attachment.att_id + "?download=true",
            });
          }
        });
        var pl_activeAttachmentID = att_id;
        var pl_attachmentViewer = new PlListDocumentViewer(
          self,
          pl_attachment,
          pl_activeAttachmentID
        );
        pl_attachmentViewer.appendTo($("body"));
      } else
        this.call("notification", "notify", {
          title: _t("File Type Not Supported"),
          message: _t("This file type can not be previewed"),
          sticky: false,
        });
    },

    willStart: async function () {
      const _super = this._super.bind(this);
      var self = this;
      // getting the attachments data
      await ajax
        .jsonRpc("/pl_list_renderer/attachments", "call", {
          res_ids: this.state.res_ids,
          model: this.state.model,
          domain: this.state.domain,
        })
        .then(function (data) {
          self.pl_data = data[0];
          self.pl_list_ = data[1];
        });
      return _super(...arguments);
    },

    updateState: async function (state, params) {
        const _super = this._super.bind(this);
        var self = this;
          await ajax
            .jsonRpc("/pl_list_renderer/attachments", "call", {
              res_ids: state.res_ids,
              model: state.model,
              domain: state.domain,
            })
            .then(function (data) {
              self.pl_data = data[0];
              self.pl_list_ = data[1];
            });
        return _super.apply(this, arguments);
    },

    _renderRow: function (record) {
      var self = this;
      var pl_attachment_limit = 5;
      var $tr = this._super.apply(this, arguments);
      if (self.pl_list_["pl_list_density"] == "Comfortable")
        $tr.addClass("pl_comfortable_list");
      else if (self.pl_list_["pl_list_density"] == "Attachment") {
        var att_data = this.pl_data;
        // adding div below the row having attachments
        if (att_data[record.data.id]) {
          var $outer_div = $("<div>", {
            class: "pl_attachment_data_outer",
          });
          var $inner_div = $("<div>", {
            class: "pl_attachment_data",
            id: record.id,
          });

          att_data[record.data.id].every((attachment, index, arr) => {
            if (index < pl_attachment_limit) {
              var $att_div = $("<div>", {
                class: "pl_attachment_id",
                "data-id": attachment.att_id,
                "data-name": attachment.att_name,
                "data-mime": attachment.att_mime,
                "data-pl-rec-id": record.data.id,
              });

              // attachment mimetype for image
              $att_div = $att_div.append(
                $("<div/>", {
                  "data-mimetype": attachment.att_mime,
                  class: "o_image",
                })
              );

              // attachment name div
              var $div_att_name = $("<div>", {
                class: "pl_attachment_name",
              }).append($("<span>").html(attachment.att_name));

              $att_div = $att_div.append($div_att_name);
              //appending both mimetype and name to the inner div
              $inner_div = $inner_div.append($att_div);
              return true;
            } else {
              var $att_div = $("<div>", {
                class: "pl_attach_counter pl_attachment_id",
                "data-id": attachment.att_id,
                "data-name": attachment.att_name,
                "data-mime": attachment.att_mime,
                "data-pl-rec-id": record.data.id,
              });
              // attachment counter div
              var $div_att_name = $("<div>", {
                class: "pl_attachment_name",
              }).append(
                $("<span>").html("+" + (arr.length - pl_attachment_limit))
              );
              $att_div = $att_div.append($div_att_name);
              //appending both mimetype and name to the inner div
              $inner_div = $inner_div.append($att_div);
              return false;
            }
          });
          var $div = $outer_div.append($inner_div);
          $tr = $tr.add($div);
        }
      }

      return $tr;
    },
    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onplAttachmentDivClicked: function (ev) {
      if (ev.target.className == "pl_attachment_data") {
        var id = $(ev.currentTarget.parentElement.previousElementSibling).data(
          "id"
        );
        if (id) {
          this.trigger_up("open_record", {
            id: id,
            target: ev.target,
          });
        }
      }
    },
    /**
     * To toggle class for adding bgcolor on selecetd rows
     * @private
     * @param {MouseEvent} ev
     */
    _onplInputChange: function (ev) {
      var self = this;
      var $plrow = ev.currentTarget.closest("tr");
      var $plparent = $plrow.parentElement.localName;
      if ($plparent == "thead") {
        var $plrows = ev.delegateTarget.querySelector("tbody").children;
        _.each($plrows, function (row) {
            if ($(row).find('td').length > 1){
                row.classList.toggle("pl_row_selected", ev.currentTarget.checked);
                self._plApplyBgColorRow(row, ev.currentTarget.checked);
            }
        });
      } else if ($plparent == "tbody"){
        $plrow.classList.toggle("pl_row_selected", ev.currentTarget.checked);
        self._plApplyBgColorRow($plrow, ev.currentTarget.checked);
      }
    },

    _plApplyBgColorRow(plRow, status){
        var self = this;
        var pl_primary = document.body.style.getPropertyValue('--primary');
        pl_primary = self._plHexToRGB(pl_primary);
        // Apply color.
        if (status){
            $(plRow).css({'background-color': `rgba(${pl_primary.r},${pl_primary.g},${pl_primary.b}, 0.3)`});
            if ($(plRow).attr('data-id')){
                $(".pl_attachment_data[id='"+$(plRow).attr('data-id')+"']").css({'background-color': `rgba(${pl_primary.r},${pl_primary.g},${pl_primary.b}, 0.3)`});
            }
        }
        // Remove color.
        else{
            $(plRow).css({'background-color': 'transparent'});
            if ($(plRow).attr('data-id')){
                $(".pl_attachment_data[id='"+$(plRow).attr('data-id')+"']").css({'background-color': 'transparent'});
            }
        }
    },

    _plHexToRGB: function (hex) {
        var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result
          ? {
              r: parseInt(result[1], 16),
              g: parseInt(result[2], 16),
              b: parseInt(result[3], 16),
            }
          : null;
      },
  });
  return Pl_ListRenderer;
});
