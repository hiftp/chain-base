# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

class ShippingBillUpdateDiscardWizard(models.TransientModel):
    _name = 'shipping.bill.update.discard.wizard'
    
    data = fields.Text('数据')

    def apply(self):
        _today = date.today()
        for i,data in enumerate(self.data.split('\n')):
            if not data:
                continue
            _datas = data.split('\t')
            if len(_datas) != 1:
                raise UserError(f'第{i+1}次 数据异常')
            _name = _datas[0]
            _name = _name.strip()

            shipping_bill = self.env['shipping.bill'].search([
                '|',('name','=',_name),('sale_fetch_no','=',_name)],limit=1)

            if not shipping_bill:
                raise UserError(f'未找到 {_name} 的单据')
            shipping_bill.write({
                'discarded_date': _today,
                'state': 'discarded',
            })
            self.env['mail.message'].create({
                'subject': '包裹已丢弃',
                'message_type': 'notification',
                'model': 'shipping.bill',
                'res_id': shipping_bill.id,
                'record_name': shipping_bill.name,
                'body': '<div>运单' + shipping_bill.name + '已被丢弃</div>'
            })
