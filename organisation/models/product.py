from odoo import fields, models, api
from random import randint
from odoo import SUPERUSER_ID
from odoo.tools import email_normalize


class Product(models.Model):
    _inherit = 'product.product'

    organisation_stage_id = fields.Many2one('organisation.stage')
