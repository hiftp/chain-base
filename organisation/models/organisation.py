# -*- coding: utf-8 -*-
"""Organisation"""


from odoo import fields, models, api
from random import randint
from odoo import SUPERUSER_ID
from odoo.tools import email_normalize
from lxml import etree
import json


class Organisation(models.Model):
    """model for managing coaches"""
    _name = "organisation.organisation"
    _description = "Organisation"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, compute='compute_organisation_name', readonly=False, store=True)
    active = fields.Boolean('Active', default=True)
    img_organisation = fields.Image()
    stage_id = fields.Many2one(
        'organisation.stage', string='Stage', index=True, tracking=True,
        readonly=False, store=True, copy=False, ondelete='restrict',
        default=lambda self: self._default_stage_id(),
        group_expand='_read_group_stage_ids')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id')
    partner_id = fields.Many2one('res.partner', string="Contact", required=True,
                                 store=True, tracking=True,
                                 domain="['|', ('company_id', '=', False), "
                                        "('company_id', '=', company_id),"
                                        "('org_group_selection', '=', False)]")
    phone = fields.Char('Phone', related='partner_id.phone', readonly=False)
    email = fields.Char('Email', related='partner_id.email', readonly=False)
    date = fields.Date(string="Report Date", default=fields.Date.today())
    responsible_user_id = fields.Many2one('res.users', string="Manager",
                                          tracking=True)
    tag_ids = fields.Many2one('organisation.tags', string="Tags")
    product_ids = fields.Many2many('product.product',
                                   'organisation_product_rel', 'product_id',
                                   'organisation_id', string="Products",
                                   compute='_compute_products', readonly=False,
                                   store=True)
    coach_ids = fields.Many2many('organisation.coaches', string="Coaches",
                                 compute='_compute_coach_ids', readonly=False,
                                 store=True)
    venue_ids = fields.Many2many('organisation.venues', string="Venues",
                                 compute='_compute_venue_ids', readonly=False,
                                 store=True)
    athlete_ids = fields.Many2many('organisation.athletes', string="Athletes",
                                   compute='_compute_athlete_ids',
                                   readonly=False, store=True)
    parent_ids = fields.Many2many('organisation.parents', string="Parents",
                                  compute='_compute_parent_ids', readonly=False,
                                  store=True)
    group_ids = fields.Many2many('athlete.groups', string="Groups", store=True,
                                 compute='_compute_group_ids', readonly=False)
    discipline_ids = fields.Many2many('organisation.discipline', store=True,
                                      string="Disciplines", readonly=False,
                                      compute='_compute_discipline_ids')
    notes = fields.Text(string="Notes")
    coaches_count = fields.Integer(compute='_compute_coaches_count', store=True)
    athletes_count = fields.Integer(compute='_compute_athletes_count',
                                    store=True)
    parents_count = fields.Integer(compute='_compute_parents_count', store=True)
    venues_count = fields.Integer(compute='_compute_venues_count', store=True)
    discipline_count = fields.Integer(compute='_compute_discipline_count',
                                      store=True)
    group_count = fields.Integer(compute='_compute_group_count', store=True)
    has_products = fields.Boolean(string="Products", default=True,
                                  help="Check if this organisation has "
                                       "PRODUCTS related")
    has_coaches = fields.Boolean(string="Coaches", default=True,
                                  help="Check if this organisation has "
                                       "COACHES related")
    has_venues = fields.Boolean(string="Venues", default=True,
                                  help="Check if this organisation has "
                                       "VENUES related")
    has_athletes = fields.Boolean(string="Athletes", default=True,
                                  help="Check if this organisation has "
                                       "ATHLETES related")
    has_parents = fields.Boolean(string="Parents", default=True,
                                 help="Check if this organisation has "
                                      "PARENTS related")
    has_fans = fields.Boolean(string="Fans", default=True,
                              help="Check if this organisation has "
                                   "FANS related")
    has_groups = fields.Boolean(string="Groups", default=True,
                                help="Check if this organisation has "
                                       "GROUPS related")
    has_disciplines = fields.Boolean(string="Discipline", default=True,
                                     help="Check if this organisation has "
                                          "DISCIPLINES related")
    is_selected_organisation = fields.Boolean(default=False)
    allowed_user_ids = fields.Many2many('res.users')
    login = fields.Char(string='Organisation Login')

    @api.depends('partner_id')
    def compute_organisation_name(self):
        for rec in self:
            print(rec, "rec")
            if rec.partner_id.sudo().company_name:
                rec.name = rec.partner_id.company_name
            else:
                rec.name = rec.partner_id.name

    @api.model
    def create(self, vals):
        """create methode"""
        result = super(Organisation, self).create(vals)
        result.partner_id.write({'org_group_selection': 'organisation'})
        user = self.env['res.users'].search(
            ['|', ('partner_id', '=', result.partner_id.id), ('login', '=', email_normalize(result.partner_id.email))])
        if not user:
            if result.stage_id.is_frontend:
                user = self.env['res.users'].with_context(
                    no_reset_password=True).create({
                    'email': email_normalize(result.partner_id.email),
                    'login': email_normalize(result.partner_id.email),
                    'partner_id': result.partner_id.id,
                    'company_id': self.env.ref('organisation.organisation_frontend_company').id,
                    'company_ids': [(6, 0, [self.env.ref('organisation.organisation_frontend_company').id])],
                })
                result.write({
                    'company_id': self.env.ref('organisation.organisation_frontend_company').id,
                })
                result.allowed_user_ids = [(6, 0, [user.id])]
                user.sudo().write({
                    'groups_id': [
                        (6, 0, [self.env.ref(
                            'organisation.group_organisation_administrator').id,
                                self.env.ref('base.group_portal').id])]
                })
            else:
                if result.stage_id.is_allowed_to_company:
                    # org_partner = result.partner_id.sudo().copy()
                    # print(org_partner, "org_partner")
                    # old_user = self.env['res.users'].sudo().search(
                    #     [('partner_id', '=', result.partner_id.id)])
                    # print(old_user, "jjjjj")
                    company = self.env['res.company'].sudo().create({
                        'name': result.name,
                        'partner_id': result.partner_id.id
                    })

                    user = self.env['res.users'].with_context(
                        no_reset_password=True).create({
                        'email': email_normalize(result.partner_id.email),
                        'login': email_normalize(result.partner_id.email),
                        'partner_id': result.partner_id.id,
                        'groups_id': [(6, 0, [self.env.ref('organisation.group_organisation_company_access').id,
                                              self.env.ref('base.group_user').id,
                                              self.env.ref('organisation.group_organisation_admins').id,
                                              self.env.ref('formio.group_formio_admin').id,
                                              self.env.ref('organisation.group_organisation_administrator').id,
                                              ])],
                        'company_id': company.id,
                        'company_ids': [(6, 0, [company.id])],
                    })
                    result.write({
                        'partner_id': result.partner_id.id,
                        'company_id': company.id,
                    })
                    result.allowed_user_ids = [(6, 0, [user.id])]
                    return result
                print(result, "ressss")
                user = self.env['res.users'].with_context(
                    no_reset_password=True).create({
                    'email': email_normalize(result.partner_id.email),
                    'login': email_normalize(result.partner_id.email),
                    'partner_id': result.partner_id.id,
                    'company_id': self.env.ref(
                        'organisation.organisation_frontend_company').id,
                    'company_ids': [(6, 0, [self.env.ref(
                        'organisation.organisation_frontend_company').id,
                                           ])],
                    'groups_id': [
                        (6, 0, [self.env.ref('base.group_user').id, self.env.ref('organisation.group_organisation_administrator').id])]
                })
                result.allowed_user_ids = [(6, 0, [user.id])]
                print(user, "name")
        else:
            if result.stage_id.is_frontend:
                user.sudo().write({
                    'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                })
                result.allowed_user_ids = [(6, 0, [user.id])]
            else:
                if result.stage_id.is_allowed_to_company:
                    old_user = self.env['res.users'].sudo().search(
                        [('partner_id', '=', result.partner_id.id)])
                    print(old_user, "jjjjj")

                    user = self.env['res.users'].with_context(
                        no_reset_password=True).create({
                        'email': email_normalize(result.partner_id.secondary_mail),
                        'login': email_normalize(result.partner_id.secondary_mail),
                        'name': result.partner_id.name,
                        'groups_id': [(6, 0, [self.env.ref('organisation.group_organisation_company_access').id,
                                              self.env.ref('base.group_user').id,
                                              self.env.ref('organisation.group_organisation_admins').id,
                                              self.env.ref('formio.group_formio_admin').id,
                                              self.env.ref('organisation.group_organisation_administrator').id,
                                              ])],

                    })
                    company = self.env['res.company'].sudo().create({
                        'name': result.name,
                        'partner_id': user.partner_id.id
                    })
                    user.write({
                        'company_id': company.id,
                        'company_ids': [(6, 0, [company.id])],
                    })
                    user.partner_id.write({
                        'org_group_selection': 'organisation'
                    })
                    print(user, "user")
                    result.write({
                        'partner_id': user.partner_id.id,
                        'company_id': company.id
                    })
                    result.allowed_user_ids = [(6, 0, [user.id, old_user.id])]
                    return result
                user.sudo().write({
                    'groups_id': [
                        (6, 0, [self.env.ref('base.group_user').id, self.env.ref('organisation.group_organisation_administrator').id])]
                })
                result.allowed_user_ids = [(6, 0, [user.id])]


        return result

    # def write(self, vals):
    #     res = super(Organisation, self).write(vals)
    #     if vals['is_selected_organisation']:
    #         self.env['organisation.organisation'].sudo().search([('partner_id', '=', self.partner_id), ])


    def _default_stage_id(self):
        """Setting default stage"""
        rec = self.env['organisation.stage'].search(
            [], limit=1, order='sequence ASC')
        return rec.id if rec else None

    @api.model
    def _read_group_stage_ids(self, categories, domain, order):
        """ Read all the stages and display it in the kanban view,
            even if it is empty."""
        category_ids = categories._search([], order=order,
                                          access_rights_uid=SUPERUSER_ID)
        return categories.browse(category_ids)

    # compute methods

    @api.depends('partner_id')
    def _compute_coach_ids(self):
        for org in self:
            coaches = self.env['organisation.coaches'].search(
                [('organisation_ids', 'in', org.id)])
            org.coach_ids = coaches

    @api.depends('coach_ids')
    def _compute_coaches_count(self):
        for org in self:
            org.coaches_count = len(org.coach_ids)

    @api.depends('partner_id')
    def _compute_venue_ids(self):
        for org in self:
            venues = self.env['organisation.venues'].search(
                [('organisation_ids', 'in', org.id)])
            org.venue_ids = venues

    @api.depends('venue_ids')
    def _compute_venues_count(self):
        for org in self:
            org.venues_count = len(org.venue_ids)

    @api.depends('partner_id')
    def _compute_athlete_ids(self):
        for org in self:
            athletes = self.env['organisation.athletes'].search(
                [('organisation_ids', 'in', org.id)])
            org.athlete_ids = athletes

    @api.depends('athlete_ids')
    def _compute_athletes_count(self):
        for org in self:
            org.athletes_count = len(org.athlete_ids)

    @api.depends('partner_id')
    def _compute_parent_ids(self):
        for org in self:
            parents = self.env['organisation.parents'].search(
                [('organisation_ids', 'in', org.id)])
            org.parent_ids = parents

    @api.depends('parent_ids')
    def _compute_parents_count(self):
        for org in self:
            org.parents_count = len(org.parent_ids)

    @api.depends('partner_id')
    def _compute_group_ids(self):
        for org in self:
            groups = self.env['athlete.groups'].search(
                [('organisation_ids', 'in', org.id)])
            org.group_ids = groups

    @api.depends('group_ids')
    def _compute_group_count(self):
        for org in self:
            org.group_count = len(org.group_ids)

    @api.depends('partner_id')
    def _compute_discipline_ids(self):
        for org in self:
            disciplines = self.env['organisation.discipline'].search(
                [('organisation_ids', 'in', org.id)])
            org.discipline_ids = disciplines

    @api.depends('discipline_ids')
    def _compute_discipline_count(self):
        for org in self:
            org.discipline_count = len(org.discipline_ids)

    def view_venues(self):
        """methode for smart button"""
        return {
            'name': "Coaches",
            'type': 'ir.actions.act_window',
            'res_model': 'organisation.venues',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.venue_ids.ids)],
            'context': {'create': False}
        }

    def view_parents(self):
        """methode for smart button"""
        return {
            'name': "Parents",
            'type': 'ir.actions.act_window',
            'res_model': 'organisation.parents',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.parent_ids.ids)],
            'context': {'create': False}
        }

    def view_athletes(self):
        """methode for smart button"""
        return {
            'name': "Athletes",
            'type': 'ir.actions.act_window',
            'res_model': 'organisation.athletes',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.athlete_ids.ids)],
            'context': {'create': False}
        }

    def view_coaches(self):
        """methode for smart button"""
        return {
            'name': "Coaches",
            'type': 'ir.actions.act_window',
            'res_model': 'organisation.coaches',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.coach_ids.ids)],
            'context': {'create': False}
        }

    def view_groups(self):
        """methode for smart button"""
        return {
            'name': "Groups",
            'type': 'ir.actions.act_window',
            'res_model': 'athlete.groups',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.group_ids.ids)],
            'context': {'create': False}
        }

    def view_disciplines(self):
        """methode for smart button"""
        return {
            'name': "Coaches",
            'type': 'ir.actions.act_window',
            'res_model': 'organisation.discipline',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.discipline_ids.ids)],
            'context': {'create': False}
        }

    @api.depends('partner_id')
    def _compute_products(self):
        for organisation in self:
            sale_orders = organisation.partner_id.sale_ids
            order_lines = sale_orders.order_line
            organisation.product_ids = order_lines.product_id


class OrganisationTags(models.Model):
    """model for managing organisation tags"""
    _name = "organisation.tags"
    _description = "Organisation Tags"
    _rec_name = 'name'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True)
    color = fields.Integer(string='Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!")]


class OrganisationStages(models.Model):
    """ Stages of Organisation """
    _name = "organisation.stage"
    _description = "Organisation Stages"
    _order = "sequence, id"
    _rec_name = "name"

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1,
                              help="Used to order stages. Lower is better.")
    description = fields.Text(string='Description', translate=True)
    fold = fields.Boolean(string='Folded in Kanban',
                          help='This stage is folded in the kanban view when '
                               'there are no records in that stage to display.')
    is_frontend = fields.Boolean('Is Frontend only?')
    is_allowed_to_company = fields.Boolean('Is allowed to create company?')
    is_subscription_allowed = fields.Boolean('Is Subscription allowed?')
    is_event_allowed = fields.Boolean('Is event allowed?')
    is_booking_allowed = fields.Boolean('Is Booking allowed?')
    is_documents_allowed = fields.Boolean('Is Documents allowed?')
    is_planning_allowed = fields.Boolean('Is Planning allowed?')
    is_diaries_allowed = fields.Boolean('Is Diaries allowed?')
    is_survey_allowed = fields.Boolean('Is Survey allowed?')
    is_forms_allowed = fields.Boolean('Is Forms allowed?')
    is_chathub_allowed = fields.Boolean('Is Chat hub allowed?')
    product_id = fields.Many2one('product.product')

    _sql_constraints = [('number_name', 'UNIQUE (name)',
                         'You can not have two stages with the same Name !')]

    @api.model
    def create(self, vals):
        res = super(OrganisationStages, self).create(vals)
        product = self.env['product.product'].sudo().create({
            'name': res.name + ' ' + 'Organisation Package',
            'organisation_stage_id': res.id,
            'detailed_type': 'service',
            'company_id': self.env.company.id
        })
        res.product_id = product.id

        return res

