
from odoo import models, fields


class Company(models.Model):
    _inherit = "res.company"

    org_id = fields.Many2one('organisation.organisation', store=True)