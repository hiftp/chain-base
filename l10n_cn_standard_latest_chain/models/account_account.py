# -*- coding: utf-8 -*-

# Created on 2018-11-28
# author: 海南贞人 |  https://www.odoochain.cn
# email: info@odoochain.cn
# resource of odooChain
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountAccount(models.Model):
    _inherit = ['account.account']
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'code'
    # _rec_name = 'complete_name'

    parent_id = fields.Many2one('account.account', 'Parent Chart', index=True, ondelete='cascade')
    child_ids = fields.One2many('account.account', 'parent_id', 'Child Chart')
    parent_path = fields.Char(index=True)

    @api.model
    def _search_new_account_code(self, company, digits, prefix):
        # 分隔符，金蝶为 "."，用友为""，注意odoo中一级科目，现金默认定义是4位头，银行是6位头
        delimiter = ''
        for num in range(1, 100):
            new_code = str(prefix.ljust(digits - 1, '0')) + delimiter + '%02d' % (num)
            rec = self.search([('code', '=', new_code), ('company_id', '=', company.id)], limit=1)
            if not rec:
                return new_code
        raise UserError(_('Cannot generate an unused account code.'))
