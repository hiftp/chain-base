# import logging

from odoo import models, fields, api, _
# from odoo.exceptions import UserError
# _logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    english_product_name = fields.Char('英文品名')
    chinese_product_name = fields.Char('中文品名')


