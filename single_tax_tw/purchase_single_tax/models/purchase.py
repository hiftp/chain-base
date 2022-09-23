#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
purchase.py

Modified taxes to single tax
"""

from odoo import models, fields, api, _, exceptions


class PurchaseOrder(models.Model):
    """
    Model of modified the purchase taxes become single tax

    [purchase.order]
    """

    _inherit = 'purchase.order'

    single_tax = fields.Many2one('account.tax', string='Tax', domain='[("type_tax_use", "=", "purchase")]', default=lambda self: self.env.company.account_purchase_tax_id)

    @api.onchange('single_tax', 'order_line', 'order_line.product_id', 'order_line.taxes_id')
    def single_tax_change(self):
        """
        When those field change will change product taxes in order line field
        """

        for order in self:
            order.order_line.taxes_id = order.single_tax

    def button_confirm(self):
        """
        When user confirm the order. Product tax will become same as single tax
        """

        self.single_tax_change()
        return super(PurchaseOrder, self).button_confirm()

    def action_rfq_send(self):
        """
        When user send the quotation of order. Product tax will become same as single tax
        """

        self.single_tax_change()
        return super(PurchaseOrder, self).action_rfq_send()
