from odoo import models, fields, api, _


class ShippingFactor(models.Model):
    _name = 'shipping.factor'
    _description = '线路敏感性'

    name = fields.Char('名称')
    currency_id = fields.Many2one('res.currency', string='币种', required=True)

    factor = fields.Float('体积重系数')
    first_weight = fields.Float('首重')
    first_total_price = fields.Float('首重总价')
    next_weight_to_ceil = fields.Float('续重取整')
    next_price_unit = fields.Float('续重单价')
    double_difference = fields.Float('倍差')

    vip_first_weight = fields.Float('SVIP首重')
    vip_first_total_price = fields.Float('SVIP首重总价')
    vip_next_weight_to_ceil = fields.Float('SVIP续重取整')
    vip_next_price_unit = fields.Float('SVIP续重单价')

    agent_first_weight = fields.Float('代理商首重')
    agent_first_total_price = fields.Float('代理商首重总价')

    vip_t_first_weight = fields.Float('VIP首重')
    vip_t_first_total_price = fields.Float('VIP首重总价')
    vip_t_next_weight_to_ceil = fields.Float('VIP续重取整')
    vip_t_next_price_unit = fields.Float('VIP续重单价')




