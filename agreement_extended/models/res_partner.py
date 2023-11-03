# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    supplier_contract_ids = fields.One2many(
        "agreement", "partner_id", string="Contracts"
    )
