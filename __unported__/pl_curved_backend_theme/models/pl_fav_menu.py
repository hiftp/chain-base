# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PlIrUiMenu(models.Model):
    _name = 'pl.fav.menu'
    _description = 'Arc Theme Favorite Menu'

    pl_fav_app = fields.Boolean(string='Fav App')
    pl_users = fields.Many2one(comodel_name='res.users')
    pl_ir_ui_menu = fields.Many2one(comodel_name='ir.ui.menu')
