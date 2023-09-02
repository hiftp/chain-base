# import logging

from odoo import models, fields, api, _
# from odoo.exceptions import UserError
# _logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_agent = fields.Boolean('代理商')


