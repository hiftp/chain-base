# import logging

from odoo import models, fields, api, _
# from odoo.exceptions import UserError
# _logger = logging.getLogger(__name__)


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    site_id = fields.Many2one('res.partner', '站点')
    site_contact_address = fields.Char(string='站点地址',related='site_id.contact_address',store=True)


