# -*- coding: utf-8 -*-
"""Coaches"""


from odoo import fields, models, api, _
from random import randint
from odoo.tools import email_normalize


class Coaches(models.Model):
    """model for managing coaches"""
    _name = "organisation.coaches"
    _description = "Coaches"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, related='partner_id.name')
    active = fields.Boolean('Active', default=True)
    img_coaches = fields.Image(related='partner_id.image_1920')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id')
    partner_id = fields.Many2one('res.partner', string="Contact", required=True,
                                 store=True, tracking=True,
                                 domain="['|', ('company_id', '=', False), "
                                        "('company_id', '=', company_id),"
                                        "('org_group_selection', '=', False)]")
    employee_id = fields.Many2one('hr.employee', string="Employee", ondelete="cascade",
                                  store=True, tracking=True)
    phone = fields.Char('Phone', related='partner_id.phone', readonly=False)
    email = fields.Char('Email', related='partner_id.email', readonly=False)
    responsible_user_id = fields.Many2one('res.users', string="Responsible",
                                          tracking=True)
    notes = fields.Text(string="Notes")
    tag_ids = fields.Many2many('coaches.tags', string="Tags")
    price_o2o = fields.Monetary(string="One to one sessions price", default=0)
    price_team = fields.Monetary(string="Team sessions price", default=0)
    organisation_ids = fields.Many2many('organisation.organisation',
                                        string="Organisations", store=True,
                                        compute='_compute_organisation_ids',
                                        readonly=False,
                                        domain=[('has_coaches', '=', True)])
    athlete_ids = fields.Many2many('organisation.athletes', store=True,
                                   readonly=False, string="Athletes",
                                   compute='_compute_athlete_ids')
    group_ids = fields.Many2many('athlete.groups', 'athlete_group_rel',
                                 'group_id', 'coach_id', string="Groups")
    task_ids = fields.Many2many('project.task', 'task_coach_rel',
                                'task_id', 'coach_id', string="Tasks",
                                compute='_compute_tasks')
    invoice_ids = fields.Many2many('account.move', 'coach_invoice_rel',
                                   'coach_id', 'invoice_id',
                                   string="Invoices",
                                   compute='_compute_invoices')
    event_ids = fields.Many2many('calendar.event', 'coach_event_rel',
                                 'coach_id', 'event_id', string="Events",
                                 compute='_compute_events')
    discipline_ids = fields.Many2many('organisation.discipline',
                                      'athlete_discipline_rel', 'athlete_id',
                                      'discipline_id', string="Disciplines",
                                      compute='_compute_disciplines')
    create_booking = fields.Boolean("Booking creation",
                                    related='partner_id.create_booking')
    document_ids = fields.One2many('athletes.documents', 'coach_id',
                                   string="Document")
    subscription_count = fields.Integer()

    _sql_constraints = [
        ('partner_uniq', 'unique (partner_id)', "You cannot create Coaches "
                                                "with same contact!")]

    # create
    @api.model
    def create(self, vals):
        """create methode"""
        result = super(Coaches, self).create(vals)
        result.partner_id.write({'org_group_selection': 'ex_coaches'})
        user = self.env['res.users'].search(
            [('partner_id', '=', result.partner_id.id)])
        if user:
            employee = self.env['hr.employee'].sudo().search(
                [('user_id', '=', user.id)], limit=1)
            if employee:
                result.employee_id = employee
            else:
                vals = {
                    'name': result.partner_id.name,
                    'company_id': result.company_id.id,
                    'address_id': result.partner_id.id,
                    'image_1920': result.partner_id.image_1920
                }
                employee = self.env['hr.employee'].create(vals)
                result.employee_id = employee
        else:
            user = self.env['res.users'].with_context(
                no_reset_password=True)._create_user_from_template({
                'email': email_normalize(result.partner_id.email),
                'login': email_normalize(result.partner_id.email),
                'partner_id': result.partner_id.id,
                'company_id': self.env.company.id,
                'company_ids': [(6, 0, self.env.company.ids)],
            })
            vals = {
                'name': result.partner_id.name,
                'company_id': result.company_id.id,
                'address_id': result.partner_id.id,
                'image_1920': result.partner_id.image_1920
            }
            user.sudo().write({
                'groups_id': [
                    (6, 0, [self.env.ref(
                        'organisation.group_organisation_coaches').id,
                            self.env.ref('base.group_portal').id])]
            })
            employee = self.env['hr.employee'].create(vals)
            result.employee_id = employee
        return result

    # unlink
    def unlink(self):
        partner = self.partner_id
        partner.org_group_selection = False
        partner.create_booking = False
        return super(Coaches, self).unlink()

    # compute methods
    @api.depends('partner_id')
    def _compute_organisation_ids(self):
        for coach in self:
            organisations = self.env['organisation.organisation'].search(
                [('coach_ids', 'in', coach.id)])
            coach.organisation_ids = organisations

    @api.depends('partner_id')
    def _compute_athlete_ids(self):
        for coach in self:
            athletes = self.env['organisation.athletes'].search(
                [('coach_ids', 'in', coach.id)])
            coach.athlete_ids = athletes

    @api.depends('partner_id')
    def _compute_tasks(self):
        for coach in self:
            tasks = self.env['project.task'].search(
                [('assign_coach_ids', 'in', [coach.id])])
            coach.task_ids = tasks

    @api.depends('partner_id')
    def _compute_disciplines(self):
        for coach in self:
            coach.discipline_ids = coach.partner_id.discipline_ids

    @api.depends('partner_id')
    def _compute_invoices(self):
        for coach in self:
            coach.invoice_ids = coach.partner_id.invoice_ids

    @api.depends('partner_id')
    def _compute_events(self):
        for coach in self:
            events = self.env['calendar.event'].search(
                [('partner_ids', 'in', coach.partner_id.id)])
            coach.event_ids = events

    def action_subscription(self):
        print("self", self)


class CoachesTags(models.Model):
    """model for managing coach tags"""
    _name = "coaches.tags"
    _description = "Coaches Tags"
    _rec_name = 'name'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True)
    color = fields.Integer(string='Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!")]
