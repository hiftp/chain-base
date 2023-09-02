# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

class ShippingBillUpdateSignWizard(models.TransientModel):
    _name = 'shipping.bill.update.sign.wizard'

    data = fields.Text('数据')

    def apply(self):
        _today = date.today()
        for i,data in enumerate(self.data.split('\n')):
            if not data:
                continue
            input = data.strip()
            shipping_bill = self.env['shipping.bill'].search([('name','=',input),('state','=','arrived')],limit=1)
            if not shipping_bill:
                shipping_bill = self.env['shipping.bill'].search([('sale_fetch_no', '=', input),
                                                                  ('state', '=', 'arrived')],limit=1)
            if not shipping_bill:
                raise UserError(f'未找到 {input} 的单据')
            shipping_bill.write({
                'signed_date': _today,
                'state': 'signed',
            })

            # 发送微信消息
            openid = shipping_bill.sale_partner_id.user_ids.wx_openid
            if openid:
                # 获取token
                token = shipping_bill.env['ir.config_parameter'].sudo().search([('key', '=', 'wechat.access_token')]).value
                tmpl_id = "0mHcAQerXuBjqJsV5ZydUTY3QfURh9m8gXojKFklGkk"
                tmpl_data = {
                    "first": {
                        "value": "您的包裹已成功签收:",
                        "color": "#173177"
                    },
                    "keyword1": {
                        "value": "%s（%s）" % (shipping_bill.picking_code, shipping_bill.name),
                        "color": "#173177"
                    },
                    "keyword2": {
                        "value": shipping_bill.sale_partner_id.name or "",
                        "color": "#173177"
                    },
                    "keyword3": {
                        "value": shipping_bill.signed_date.strftime('%Y-%m-%d') or "",
                        "color": "#173177"
                    },
                    "remark": {
                        "value": "感谢您的使用。期待您下次使用。",
                        "color": "#173177"
                    },
                }
                shipping_bill.wx_information_send(token, openid, tmpl_data, tmpl_id)

            # 发送邮件
            self.env.ref('shipping_bills.mail_template_data_shipping_bill_sign_for').send_mail(shipping_bill.id, force_send=True)

            # 发送短信
            if shipping_bill.sale_partner_id.phone:
                msg = 'Successful delivery for package [%s]. It has been signed for. ' \
                      'For any feedback or assistance, reach out to our customer service.     Sinefine' % (
                          shipping_bill.tracking_no)
                shipping_bill.send_message_post(msg)
