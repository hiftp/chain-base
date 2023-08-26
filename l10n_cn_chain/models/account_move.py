# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

try:
    from cn2an import an2cn
except ImportError:
    an2cn = None

class AccountMove(models.Model):
    _inherit = 'account.move'

