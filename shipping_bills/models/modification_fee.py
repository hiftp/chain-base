from odoo import models, fields, api, _


class ModificationFee(models.Model):
    _name = 'modification.fee'
    _description = '改泡费'

    name = fields.Char('名称')
    price = fields.Float('价格')
    currency_id = fields.Many2one('res.currency', string="币种")

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        self.price = self.price * self.currency_id.rate

