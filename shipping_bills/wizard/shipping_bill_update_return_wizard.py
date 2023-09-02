# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

class ShippingBillUpdateReturnWizard(models.TransientModel):
    _name = 'shipping.bill.update.return.wizard'
    
    data = fields.Text('数据')

    def apply(self):
        _today = date.today()
        for i,data in enumerate(self.data.split('\n')):
            if not data:
                continue
            _datas = data.split('\t')
            if len(_datas) != 2:
                raise UserError(f'第{i+1}次 数据异常')
#            name, return_address, return_contact, return_mobile, return_name = _datas
#            name, return_address, return_contact, return_mobile, return_name = name.strip(),\
#                    return_address.strip(), return_contact.strip(), return_mobile.strip(),\
#                     return_name.strip(),  
            
            _name, return_name = _datas
            _name, return_name = _name.strip(), return_name.strip(),

            shipping_bill = self.env['shipping.bill'].search([
                '|',('name','=',_name),('sale_fetch_no','=',_name),('state','=','valued')],limit=1)

            if not shipping_bill:
                raise UserError(f'未找到 {_name} 的单据')
            shipping_bill.write({
                'returned_date': _today,
                'state': 'returned',
#                'return_address': return_address,
#                'return_contact': return_contact,
#                'return_mobile': return_mobile,
                'return_name': return_name,
            })

            # 发送微信消息
            openid = shipping_bill.sale_partner_id.user_ids.wx_openid
            # 获取token
            token = self.env['ir.config_parameter'].sudo().search([('key', '=', 'wechat.access_token')]).value
            if openid:
                tmpl_id = "3yfETXzY9V-3xPLWlxOGc7ItkNWPLCyusqKaLQkQgDI"
                tmpl_data = {
                    "first": {
                        "value": "尊敬的客户" + ' ' + shipping_bill.sale_partner_id.name + ',' + '您的包裹已退运。',
                        "color": "#173177"
                    },
                    "keyword1": {
                        "value": shipping_bill.name or "",
                        "color": "#173177"
                    },
                    "keyword2": {
                        "value": shipping_bill.shipping_factor_id.name or "",
                        "color": "#173177"
                    },
                    "keyword3": {
                        "value": "订单已退运",
                        "color": "#173177"
                    },
                    "remark": {
                        "value": "退运快递单号：" + shipping_bill.tracking_no or "",
                        "color": "#173177"
                    },
                }
                shipping_bill.wx_information_send(token, openid, tmpl_data, tmpl_id)

