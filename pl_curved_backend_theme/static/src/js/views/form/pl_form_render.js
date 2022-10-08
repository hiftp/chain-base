odoo.define("pl_curved_backend_theme.pl_form_renderer", function (require) {
  "use strict";

  var FormRenderer = require("web.FormRenderer");

  var Pl_FormRenderer = FormRenderer.include({
    // FixMe: Remove before in case of no events
    events: _.extend({}, FormRenderer.prototype.events, {}),
    /**
     * @override
     * To bind this with pl_form_resize
     */
    init: function () {
      this._super.apply(this, arguments);
      this.pl_from_resize = _.debounce(this.pl_from_resize.bind(this), 200);
    },
    /**
     * @override
     */
    start() {
      window.addEventListener("resize", this.pl_from_resize);
      return this._super(...arguments);
    },
    /**
     * @override
     */
    destroy() {
      window.removeEventListener("resize", this.pl_from_resize);
      return this._super(...arguments);
    },
    /**
     * @override
     */
    _applyFormSizeClass: function () {
      this.pl_from_resize();
      return this._super(...arguments);
    },
    /**
     * ## Already Handled in ENTERPRISE
     * To add and remove classes for chatter position
     */
    pl_from_resize() {
      if (
        window.matchMedia("(min-width: 1400px)").matches &&
        this?.$el[0].classList.contains("o_form_view")
      )
        this?.$el[0].classList.add("pl_large_screen");
      else if (this?.$el[0].classList.contains("pl_large_screen"))
        this?.$el[0].classList.remove("pl_large_screen");
    },
  });
  return Pl_FormRenderer;
});
