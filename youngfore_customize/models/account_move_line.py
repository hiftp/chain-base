# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    ap_type = fields.Char(string="帳款分類", required=False, )
    purchase_no = fields.Char(string="進貨單號", required=False, )
    purchase_date = fields.Char(string="進貨日期", required=False, )
    bill_no = fields.Char(string="發票號碼", required=False, )
    bill_date = fields.Char(string="發票日期", required=False, )
    import_memo = fields.Char(string="匯入資訊", required=False, )

    @api.onchange('invoice_payment_ref')
    def _onchange_invoice_payment_ref(self):
        date_ym = str(self.date.year)+'/'+ str(self.date.month)
        for line in self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')):
            line.name = self.partner_id.name+' '+date_ym+' '+self.invoice_payment_ref

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('account_id')
    def _onchange_account_id(self):
        if self.account_id:
            if self.account_id.analytic_tag_ids:
                self.analytic_tag_ids = [(6, 0, self.account_id.analytic_tag_ids.ids)]
        return super(AccountMoveLine, self)._onchange_account_id()
