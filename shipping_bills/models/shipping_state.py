from odoo import models, fields, api, _


class ShippingState(models.Model):
    _name = 'shipping.state'
    _description = '阶段'
    _rec_name = 'name'
    _order = 'sequence'

    name = fields.Char('名称')
    state = fields.Selection([('draft', '草稿'), ('paired', '已匹配'), ('valued', '已计费'), ('payment', '已支付'),
                              ('returned', '已退运'), ('transported', '已转运'), ('arrived', '已到站点'),
                              ('signed', '已签收'), ('discarded', '丢弃')], default='draft', string='状态')
    fold = fields.Boolean('是否在看板中折叠')
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order when displaying a list of stages.")
    requirements = fields.Text("Requirements")

