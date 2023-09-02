
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shipping_no = fields.Char(string='运单号',copy=False)
    fetch_no = fields.Char(string='取件码')
    partner_team_site_id = fields.Many2one('res.partner', string='站点', store=True)

    @api.onchange('partner_id')
    def onchange_partner_team_site_id(self):
        self.partner_team_site_id = self.partner_id.team_id.site_id.id

    partner_team_site_contact_address = fields.Char(string='站点地址',related='partner_team_site_id.contact_address',store=True)

    shipping_bill_id = fields.Many2one('shipping.bill')
    shipping_bill_state = fields.Selection(related='shipping_bill_id.state',store=True)

    no_change = fields.Boolean('免泡')

    @api.constrains('shipping_no')
    def check_shipping_no_unique(selfs):
        for self in selfs:
            if self.shipping_no:
                if selfs.search_count([('shipping_no','=',self.shipping_no),('id','!=',self.id)]):
                    raise UserError(f'运单号 {self.shipping_no} 已存在')

#    def set_fetch_no(self):
#        if self.fetch_no:
#            return
#        country_code = self.partner_team_site_id.country_code
#        if not country_code:
#            raise UserError('请先维护客户的国家编码')
#        site_code = self.partner_team_site_id.ref
#        if not site_code:
#            raise UserError('请先维护站点编码')
#        sequence = self.env['ir.sequence'].next_by_code('sale.fetch.no')
#        self.fetch_no = f'{country_code}{site_code}{sequence}'
#

