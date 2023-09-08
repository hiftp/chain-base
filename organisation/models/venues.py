# -*- coding: utf-8 -*-
"""Venues"""


from odoo import fields, models, api, _
from random import randint


class Venues(models.Model):
    """model for managing venues"""
    _name = "organisation.venues"
    _description = "Venues"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, related='partner_id.name')
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id')
    partner_id = fields.Many2one('res.partner', string="Contact", required=True,
                                 store=True, tracking=True,
                                 domain="['|', ('company_id', '=', False), "
                                        "('company_id', '=', company_id)]")
    phone = fields.Char('Phone', related='partner_id.phone', readonly=False)
    email = fields.Char('Email', related='partner_id.email', readonly=False)
    date = fields.Date(string="Date", default=fields.Date.today())
    organisation_ids = fields.Many2many('organisation.organisation', store=True,
                                        compute='_compute_organisation_ids',
                                        readonly=False, string="Organisation",
                                        domain=[('has_venues', '=', True)])
    responsible_user_id = fields.Many2one('res.users', string="Responsible",
                                          tracking=True)
    tag_ids = fields.Many2many('venues.tags', string="Tags")

    # compute methods
    @api.depends('partner_id')
    def _compute_organisation_ids(self):
        for venue in self:
            organisations = self.env['organisation.organisation'].search(
                [('venue_ids', 'in', venue.id)])
            venue.organisation_ids = organisations


class VenuesTags(models.Model):
    """model for managing venue tags"""
    _name = "venues.tags"
    _description = "Venues Tags"
    _rec_name = 'name'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True)
    color = fields.Integer(string='Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!")]
