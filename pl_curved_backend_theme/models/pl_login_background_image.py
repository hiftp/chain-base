# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class PlLoginBackgroundImage(models.Model):
    _name = 'pl.login.background.image'
    _description = 'Arc Theme Login Background Image'

    pl_image = fields.Binary(string="Image")
    pl_active = fields.Boolean(string="Background selected")
