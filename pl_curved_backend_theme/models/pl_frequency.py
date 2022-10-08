from odoo import models, fields


class PlFrequnencyCounter(models.Model):
    _name = "pl.frequency.counter"
    _description = "Apps Frequency"

    pl_frequency = fields.Integer(string="Frequency", default=0)
    pl_user_id = fields.Many2one(string="User", comodel_name="res.users", required=True, help="Connected User")
    pl_menu_id = fields.Many2one(string="Menu", comodel_name="ir.ui.menu", required=True, help="Menu List")