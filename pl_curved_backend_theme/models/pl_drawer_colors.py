# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class PlDrawerColors(models.Model):
    _name = 'pl.drawer.colors'
    _description = 'Arc Theme App Drawer Colors'

    pl_colors = fields.Char(string='Colors')
    pl_font_style = fields.Selection(selection=[('light', 'Light'), ('dark', 'Dark')],
                                     string='Font style')
    pl_no_delete = fields.Boolean(string='Default colors')
