# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class PlLoginBackgroundColor(models.Model):
    _name = 'pl.login.background.color'
    _description = 'Arc Theme Login Background Color'

    pl_color = fields.Char(string="Color")
    pl_active = fields.Boolean(string="Background selected")
