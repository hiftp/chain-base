# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='分析標籤')
