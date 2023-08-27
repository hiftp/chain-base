# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class PlBodyBackground(models.Model):
    _name = 'pl.body.background'
    _description = 'Arc Theme Body Background'

    pl_image = fields.Binary(string="Image")
    pl_user = fields.Many2one(string="User", comodel_name="res.users")
    pl_company = fields.Many2one(string="Company", comodel_name="res.company")
    pl_global = fields.Boolean(string="Global")
    pl_active = fields.Boolean(string="Background selected")
