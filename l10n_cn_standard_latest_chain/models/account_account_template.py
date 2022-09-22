# -*- coding: utf-8 -*-

# Created on 2018-11-28
# author: 海南贞人 |  https://www.odoochain.cn
# email: info@odoochain.cn
# resource of odooChain
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, exceptions, _

class AccountAccountTemplate(models.Model):

    _inherit = ['account.account.template']
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'code'
    # _rec_name = 'complete_name'

    parent_id = fields.Many2one('account.account.template', 'Parent Chart', index=True, ondelete='cascade')
    child_ids = fields.One2many('account.account.template', 'parent_id', 'Child Chart')
    parent_path = fields.Char(index=True)


