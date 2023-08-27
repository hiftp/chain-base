odoo.define("pl_curved_backend_theme.AbstractWebClient", function (require) {
  "use strict";

  var { WebClient } = require("@web/webclient/webclient");
  var session = require("web.session");
  var ajax = require("web.ajax");

  const { hoopl } = owl;

  var { patch } = require("web.utils");
  patch(WebClient.prototype, "AbstractWebClient", {
    async setup() {
      /**
       * Set webpage title if user has selected.
       */
      this._super();
      const plTitle = await this.env.services.rpc(
        "/pl_curved_theme/pl_get_website_title"
      );

        const manifest =  await this.env.services.rpc("/pl_curved_backend_theme/get_manifest").then(
        function (result) {
          if (result){
              let encodeData = encodeURIComponent(JSON.stringify(result));
              let manifestURL = "data:application/manifest+json," + encodeData;
              let manifestElement = document.createElement("link");
              manifestElement.setAttribute("rel", "manifest");
              manifestElement.setAttribute("href", manifestURL);
              document.querySelector("head").appendChild(manifestElement);
          }
        }
      )

      if (plTitle)
        this.title.setParts({ zopenerp: plTitle });





//      await ajax
//        .jsonRpc({ route: "/pl_curved_backend_theme/get_manifest" }).then(
//        function (result) {
//          if (result){
//              let encodeData = encodeURIComponent(JSON.stringify(result));
//              let manifestURL = "data:application/manifest+json," + encodeData;
//              let manifestElement = document.createElement("link");
//              manifestElement.setAttribute("rel", "manifest");
//              manifestElement.setAttribute("href", manifestURL);
//              document.querySelector("head").appendChild(manifestElement);
//          }
//        }
//      )
    },

  });
});
