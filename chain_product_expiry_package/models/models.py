# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.move.line'

    expiration_date_package = fields.Date(string="Expiration Date Packaging")

