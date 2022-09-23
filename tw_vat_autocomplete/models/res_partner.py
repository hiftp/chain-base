import requests
from odoo import models, api
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('name', 'country_id')
    def _fetch_tw_vat(self):
        country_tw = self.env.ref('base.tw')
        if not self.is_company:
            return
        if self.vat:
            return
        if not self.name:
            return
        if self.country_id != country_tw:
            return
        url = 'https://data.gcis.nat.gov.tw/od/data/api/6BBA2268-1367-4B42-9CCA-BC17499EBE8C?$format=json&$filter=Company_Name like %s and Company_Status eq 01&$skip=0&$top=1' % self.name
        try:
            response = requests.get(url)
            res_data = response.json()
        except Exception as e:
            raise UserError(e)
        vat = res_data[0].get('Business_Accounting_NO', '')
        self.vat = vat

    @api.onchange('vat', 'country_id')
    def _fetch_tw_name(self):
        """
        When tax id or country id change use tax id to search company name from api.
        """
        country_tw = self.env.ref('base.tw')
        if not self.is_company:
            return
        if self.name:
            return
        if not self.vat:
            return
        if self.country_id != country_tw:
            return
        url = 'https://data.gcis.nat.gov.tw/od/data/api/9D17AE0D-09B5-4732-A8F4-81ADED04B679?$format=json&$filter=Business_Accounting_NO eq %s&$skip=0&$top=1' % self.vat
        try:
            response = requests.get(url)
            res_data = response.json()
        except Exception as e:
            raise UserError(e)
        name = res_data[0].get('Company_Name', '')
        self.name = name
