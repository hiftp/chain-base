# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class PlDrawerBackground(models.Model):
    _name = 'pl.drawer.background'
    _description = 'Arc Theme App Drawer Background'

    pl_image = fields.Binary(string="Image")
    pl_user = fields.Many2one(string="User", comodel_name="res.users")
    pl_company = fields.Many2one(string="Company", comodel_name="res.company")
    pl_global = fields.Boolean(string="Global")
    pl_active = fields.Boolean(string="Background selected")
