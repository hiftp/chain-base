from odoo import models, fields, api, _


class PlIrConfig(models.Model):
    _inherit = 'ir.config_parameter'

    pl_enterprise_apps = fields.Boolean(string="Hide Enterprise Apps", default=False)
    pl_odoo_referral = fields.Boolean(string="Show Odoo Referral", default=False)
    pl_login_design = fields.Selection(string="", selection=[('default', 'Default'), ('login_style_1', 'Style 1')],
                                       default='default')
    pl_login_background = fields.Binary(string="Login Background Image")