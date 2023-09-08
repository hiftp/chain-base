# -*- coding: utf-8 -*-
"""Discipline"""


from odoo import fields, models, api
from random import randint
from odoo import SUPERUSER_ID


class Disciplines(models.Model):
    """model for managing Discipline"""
    _name = "organisation.discipline"
    _description = "Discipline"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True,
                       related='partner_id.name')
    active = fields.Boolean('Active', default=True)
    stage_id = fields.Many2one(
        'discipline.stage', string='Stage', index=True, tracking=True,
        readonly=False, store=True, copy=False, ondelete='restrict',
        default=lambda self: self._default_stage_id(),
        group_expand='_read_group_stage_ids')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id')
    partner_id = fields.Many2one('res.partner', string="Contact",
                                 store=True, tracking=True)
    user_id = fields.Many2one('res.users', string="User", required=False,
                              store=True, tracking=True)
    phone = fields.Char('Phone', related='user_id.partner_id.phone',
                        readonly=False)
    email = fields.Char('Email', related='user_id.partner_id.email',
                        readonly=False)
    responsible_user_id = fields.Many2one('res.users', string="Responsible",
                                          tracking=True)
    tag_ids = fields.Many2many('discipline.tags', string="Tags")
    athlete_ids = fields.Many2many('organisation.athletes', string="Athletes",
                                   store=True, readonly=False,
                                   compute='_compute_athlete_ids')
    organisation_ids = fields.Many2many('organisation.organisation', store=True,
                                        compute='_compute_organisation_ids',
                                        readonly=False, string="Organisation",
                                        domain=[('has_disciplines', '=', True)])

    def _default_stage_id(self):
        """Setting default stage"""
        rec = self.env['discipline.stage'].search(
            [], limit=1, order='sequence ASC')
        return rec.id if rec else None

    @api.model
    def _read_group_stage_ids(self, categories, domain, order):
        """ Read all the stages and display it in the kanban view,
            even if it is empty."""
        category_ids = categories._search([], order=order,
                                          access_rights_uid=SUPERUSER_ID)
        return categories.browse(category_ids)

    # compute methode
    @api.depends('partner_id')
    def _compute_organisation_ids(self):
        for discipline in self:
            organisations = self.env['organisation.organisation'].search(
                [('discipline_ids', 'in', discipline.id)])
            discipline.organisation_ids = organisations

    @api.depends('partner_id')
    def _compute_athlete_ids(self):
        for discipline in self:
            athletes = self.env['organisation.athletes'].search(
                [('discipline_ids', 'in', discipline.id)])
            discipline.athlete_ids = athletes


class DisciplineTags(models.Model):
    """model for managing Discipline tags"""
    _name = "discipline.tags"
    _description = "Discipline Tags"
    _rec_name = 'name'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True)
    color = fields.Integer(string='Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!")]


class DisciplineStages(models.Model):
    """ Stages of Discipline """
    _name = "discipline.stage"
    _description = "Discipline Stages"
    _order = "sequence, id"
    _rec_name = "name"

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1,
                              help="Used to order stages. Lower is better.")
    description = fields.Text(string='Description', translate=True)
    fold = fields.Boolean(string='Folded in Kanban',
                          help='This stage is folded in the kanban view when '
                               'there are no records in that stage to display.')

    _sql_constraints = [('number_name', 'UNIQUE (name)',
                         'You can not have two stages with the same Name !')]
