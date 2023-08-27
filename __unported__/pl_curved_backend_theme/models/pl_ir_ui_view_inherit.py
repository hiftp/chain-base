from odoo import models, fields, _


class PlView(models.Model):
    _inherit = "ir.ui.view"

    pl_users = fields.One2many(inverse_name='pl_ir_ui_view', comodel_name="res.users", string='User')
    pl_users_ids = fields.Many2many(comodel_name="res.users", string='Users')
