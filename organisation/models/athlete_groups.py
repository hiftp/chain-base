# -*- coding: utf-8 -*-
"""Athlete Groups"""


from odoo import fields, models, api
from random import randint


class AthleteGroups(models.Model):
    """model for managing athletes"""
    _name = "athlete.groups"
    _description = "Athlete Groups"
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
    responsible_user_id = fields.Many2one('res.users', string="Responsible",
                                          tracking=True)
    tag_ids = fields.Many2many('group.tags', string="Tags")
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist",
                                   tracking=True)
    athlete_ids = fields.Many2many('organisation.athletes', string="Athletes",
                                   readonly=False, store=True,
                                   compute='_compute_athlete_ids')
    document_ids = fields.One2many('athletes.documents',
                                   'group_id', string="Document")
    organisation_ids = fields.Many2many('organisation.organisation', store=True,
                                        compute='_compute_organisation_ids',
                                        readonly=False, string="Organisation",
                                        domain=[('has_groups', '=', True)])

    # compute methode
    @api.depends('partner_id')
    def _compute_organisation_ids(self):
        for group in self:
            organisations = self.env['organisation.organisation'].search(
                [('group_ids', 'in', group.id)])
            group.organisation_ids = organisations

    @api.depends('partner_id')
    def _compute_athlete_ids(self):
        for group in self:
            athletes = self.env['organisation.athletes'].search(
                [('group_ids', 'in', group.id)])
            group.athlete_ids = athletes


class GroupsTags(models.Model):
    """model for managing group tags"""
    _name = "group.tags"
    _description = "Groups Tags"
    _rec_name = 'name'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True)
    color = fields.Integer(string='Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!")]
