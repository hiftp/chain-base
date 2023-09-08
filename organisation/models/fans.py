# -*- coding: utf-8 -*-
"""Fans"""


from odoo import fields, models, api
from random import randint
from odoo.tools import email_normalize
import string
import random


class Fans(models.Model):
    """model for managing Fans"""
    _name = "organisation.fans"
    _description = "Fans"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    def _get_default_organisation(self):
        config_settings = self.env['res.config.settings'].search([], limit=1)
        default_org = config_settings.default_org_id or False
        return default_org

    name = fields.Char(string="Name", required=True, related='partner_id.name')
    active = fields.Boolean('Active', default=True)
    img_fan = fields.Image()
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id')
    # partner_id = fields.Many2one('res.partner')
    partner_id = fields.Many2one('res.partner', string="Contact", required=True,
                                 store=True, tracking=True,
                                 domain="['|', ('company_id', '=', False), "
                                        "('company_id', '=', company_id),"
                                        "('org_group_selection', '=', False)]")
    phone = fields.Char('Phone', related='partner_id.phone', readonly=False)
    email = fields.Char('Email', related='partner_id.email', readonly=False)
    date = fields.Date(string="Date", default=fields.Date.today())
    organisation_id = fields.Many2one('organisation.organisation', store=True,
                                      string="Organisation",
                                      domain=[('has_fans', '=', True)],
                                      default=_get_default_organisation)
    tag_ids = fields.Many2many('fans.tags', string="Tags")
    # athlete_ids = fields.Many2many('organisation.athletes',
    #                                'parent_athlete_rel', 'athlete_id',
    #                                'parent_id', string="Parents")
    create_booking = fields.Boolean("Booking creation",
                                    related='partner_id.create_booking')
    event_ids = fields.Many2many('calendar.event', 'fan_event_rel',
                                 'fan_id', 'event_id', string="Events",
                                 compute='_compute_events')
    conf_create_athlete = fields.Boolean(string="Create Athlete", readonly=True,
                                         compute='_compute_conf_create_athlete')

    _sql_constraints = [
        ('partner_uniq', 'unique (partner_id)', "You cannot create "
                                                "Fans with same contact!")]

    def action_create_athlete(self):
        partner = self.partner_id
        self.unlink()
        pin = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=6))
        config_settings = self.env['res.config.settings'].search([], limit=1)
        organisation = config_settings.default_org_id
        athlete = self.env['organisation.athletes'].create({
            'partner_id': partner.id,
            'member_id': str(pin),
            # 'organisation_ids': [(4, organisation.id)],
        })
        athlete.organisation_ids = organisation
        return {
            'name': "Athletes",
            'type': 'ir.actions.act_window',
            'res_model': 'organisation.athletes',
            'view_mode': 'form',
            'res_id': athlete.id,
            'target': 'main',
        }

    # create
    @api.model
    def create(self, vals):
        """create methode"""
        result = super(Fans, self).create(vals)
        result.partner_id.write({'org_group_selection': 'fans',
                                 'create_booking': True,
                                 })
        user = self.env['res.users'].search(
            [('partner_id', '=', result.partner_id.id)])
        if not user:
            user = self.env['res.users'].with_context(
                no_reset_password=True)._create_user_from_template({
                'email': email_normalize(result.partner_id.email),
                'login': email_normalize(result.partner_id.email),
                'partner_id': result.partner_id.id,
                'company_id': self.env.company.id,
                'company_ids': [(6, 0, self.env.company.ids)],
            })
            user.sudo().write({
                'groups_id': [
                    (6, 0, [self.env.ref(
                        'organisation.group_organisation_fans').id,
                            self.env.ref('base.group_portal').id])]
            })
        return result

    # unlink
    def unlink(self):
        partner = self.partner_id
        partner.org_group_selection = False
        partner.create_booking = False
        return super(Fans, self).unlink()

    # compute methods
    @api.depends('partner_id')
    def _compute_events(self):
        for fan in self:
            events = self.env['calendar.event'].search(
                [('partner_ids', 'in', fan.partner_id.id)])
            fan.event_ids = events

    def _compute_conf_create_athlete(self):
        params = self.env['ir.config_parameter'].sudo()
        create_athlete = params.get_param('organisation.athlete_from_fan')
        for rec in self:
            rec.conf_create_athlete = create_athlete


class FansTags(models.Model):
    """model for managing fans tags"""
    _name = "fans.tags"
    _description = "Fans Tags"
    _rec_name = 'name'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True)
    color = fields.Integer(string='Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!")]
