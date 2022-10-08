from odoo import _, api, exceptions, fields, models
import base64
from odoo.tools.mimetypes import guess_mimetype


class PlResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def _default_global_config(self):
        return self.env.ref('pl_curved_backend_theme.pl_global_config_single_rec')

    pl_enable_pwa_app = fields.Boolean(string="Enable PWA",
                                       config_parameter='pl_curved_backend_theme.pl_enable_pwa_app', default=True)
    pl_pwa_name = fields.Char(string="Pl PWA Name", config_parameter='pl_curved_backend_theme.pl_pwa_name', default='Saltfun')
    pl_global_config = fields.Many2one(comodel_name='pl.global.config',
                                       config_parameter='pl_curved_backend_theme.pl_global_config')
    pl_pwa_icon = fields.Binary(related='pl_global_config.pl_pwa_icon', readonly=False, string="Icon")
    pl_pwa_short_name = fields.Char(string="Pl PWA ShortName", config_parameter='pl_curved_backend_theme.pl_pwa_short_name')

    pl_pwa_background_color = fields.Char(string="PWA Background Color",
                                          config_parameter='pl_curved_backend_theme.pl_pwa_background_color')
    pl_pwa_theme_color = fields.Char(string="PWA Theme Theme Color",
                                     config_parameter='pl_curved_backend_theme.pl_pwa_theme_color')

    @api.model
    def get_values(self):
        res = super(PlResConfigSettings, self).get_values()

        # Check if global setting field has no data then assign the default the global setting record.
        if not self.pl_global_config:
            res.update(pl_global_config=self.env.ref('pl_curved_backend_theme.pl_global_config_single_rec').id)

        pl_pwa_icon = self.env.ref('pl_curved_backend_theme.pl_global_config_single_rec').sudo().pl_pwa_icon
        res.update(
            pl_pwa_icon=pl_pwa_icon if pl_pwa_icon else False,
        )
        return res
