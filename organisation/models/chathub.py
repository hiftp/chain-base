# -*- coding: utf-8 -*-
"""Chathub"""


from odoo import fields, models


class Chathub(models.Model):
    """model for managing chathub channels"""
    _name = "chat.hub"
    _description = "Chat-hub"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, copy=False)
    description = fields.Text(string="Description", copy=False)
    partner_ids = fields.Many2many('res.partner', 'partner_chat_hub_rel',
                                   'partner_id', 'chat_hub_id',
                                   string="Members", copy=False, store=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

