# -*- coding: utf-8 -*-
"""Athletes"""


from odoo import fields, models, api
from random import randint
from odoo.tools import email_normalize
from dateutil.relativedelta import relativedelta


class Athletes(models.Model):
    """model for managing athletes"""
    _name = "organisation.athletes"
    _description = "Athletes"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, related='partner_id.name')
    active = fields.Boolean('Active', default=True)
    img_athletes = fields.Image(related='partner_id.image_1920')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id')
    partner_id = fields.Many2one('res.partner', string="Contact", required=True,
                                 store=True, tracking=True,
                                 domain="['|', ('company_id', '=', False), "
                                        "('company_id', '=', company_id), "
                                        "('org_group_selection', '=', False)]")
    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  ondelete="cascade", store=True, tracking=True)
    member_id = fields.Char(string="Member ID", store=True)
    phone = fields.Char('Phone', related='partner_id.phone', readonly=False)
    email = fields.Char('Email', related='partner_id.email', readonly=False)
    date = fields.Date(string="Date", default=fields.Date.today())
    dob = fields.Date(string="DOB", )
    age = fields.Integer(string="Age", compute='_compute_age', store=True)
    organisation_ids = fields.Many2many('organisation.organisation', store=True,
                                        compute='_compute_organisation_ids',
                                        readonly=False, string="Organisations",
                                        domain=[('has_athletes', '=', True)])
    tag_ids = fields.Many2many('athletes.tags', string="Tags", store=True)
    parent_ids = fields.Many2many('organisation.parents', string="Parents",
                                  compute='_compute_parent_ids', readonly=False,
                                  store=True)
    discipline_ids = fields.Many2many('organisation.discipline', store=True,
                                      string="Disciplines", readonly=False,
                                      compute='_compute_disciplines')
    group_ids = fields.Many2many('athlete.groups', store=True,
                                 compute='_compute_group_ids',
                                 readonly=False, string="Groups")
    coach_ids = fields.Many2many('organisation.coaches', string="Coaches",
                                 store=True, compute='_compute_coach_ids',
                                 readonly=False)
    responsible_user_id = fields.Many2one('res.users', string="Responsible",
                                          tracking=True)
    assigned_partner_id = fields.Many2one('res.partner', string="Assigned to",
                                          related='partner_id')
    form_ids = fields.Many2many('formio.form', 'athlete_form_rel',
                                'athlete_id', 'form_id', string="Forms")
    survey_ids = fields.Many2many('survey.survey', 'athlete_survey_rel',
                                  'athlete_id', 'survey_id', string="Surveys")
    product_ids = fields.Many2many('product.product', string="Product",
                                   compute='_compute_products', readonly=False)
    invoice_ids = fields.Many2many('account.move', 'athlete_invoice_rel',
                                   'athlete_id', 'invoice_id', string="Invoices",
                                   compute='_compute_invoices')
    event_ids = fields.Many2many('calendar.event', 'athlete_event_rel',
                                 'athlete_id', 'event_id', string="Events",
                                 compute='_compute_events')
    document_ids = fields.One2many('athletes.documents', 'athlete_id',
                                   string="Document")
    task_ids = fields.Many2many('project.task', 'task_athlete_rel',
                                'task_id', 'athlete_id', string="Tasks",
                                compute='_compute_tasks')
    create_booking = fields.Boolean("Booking creation",
                                    related='partner_id.create_booking')
    vehicle_ids = fields.Many2many('vehicle.registration', readonly=False,
                                   string="Vehicle Registration", store=True,
                                   compute='_compute_vehicle_ids')
    conf_create_fan = fields.Boolean(string="Create Fan", readonly=True,
                                     compute='_compute_conf_create_fan')


    _sql_constraints = [
        ('partner_uniq', 'unique (partner_id)', "You cannot create Athletes "
                                                "with same contact!")]

    # create
    @api.model
    def create(self, vals):
        """create methode"""
        if not vals.get('member_id'):
            vals['member_id'] = self.env['ir.sequence'].next_by_code(
                'organisation.athletes')
        result = super(Athletes, self).create(vals)
        result.partner_id.write({'org_group_selection': 'athletes',
                                 'athlete_id': result.id,
                                 'dob': result.dob})
        user = self.env['res.users'].search(
            [('partner_id', '=', result.partner_id.id)])
        if user:
            employee = self.env['hr.employee'].sudo().search(
                [('user_id', '=', user.id)], limit=1)
            if employee:
                employee.generate_random_barcode()
                result.employee_id = employee
                employee.athlete_id = result.id
            else:
                vals = {
                    'name': result.partner_id.name,
                    'company_id': result.company_id.id,
                    'address_id': result.partner_id.id,
                    'image_1920': result.partner_id.image_1920,
                    'member_id': result.member_id
                }
                employee = self.env['hr.employee'].create(vals)
                employee.generate_random_barcode()
                result.employee_id = employee
                employee.athlete_id = result.id
        else:
            user = self.env['res.users'].sudo().with_context(
                no_reset_password=True)._create_user_from_template({
                'email': email_normalize(result.partner_id.email),
                'login': email_normalize(result.partner_id.email),
                'partner_id': result.partner_id.id,
                'company_id': self.env.company.id,
                'company_ids': [(6, 0, self.env.company.ids)],
            })
            # user.action_reset_password()
            vals = {
                'name': result.partner_id.name,
                'company_id': result.company_id.id,
                'address_id': result.partner_id.id,
                'image_1920': result.partner_id.image_1920,
                'member_id': result.member_id
            }
            user.sudo().write({
                'groups_id': [
                    (6, 0, [self.env.ref('organisation.group_organisation_athletes').id, self.env.ref('base.group_portal').id])]
            })
            employee = self.env['hr.employee'].create(vals)
            employee.generate_random_barcode()
            result.employee_id = employee
            employee.athlete_id = result.id
        return result

    # write
    def write(self, vals):
        res = super(Athletes, self).write(vals)
        if 'dob' in vals:
            self.partner_id.dob = vals['dob']
        return res

    # unlink
    def unlink(self):
        partner = self.partner_id
        partner.org_group_selection = False
        partner.create_booking = False
        return super(Athletes, self).unlink()

    def action_create_fan(self):
        partner = self.partner_id
        self.unlink()
        fan = self.env['organisation.fans'].create({
            'partner_id': partner.id,
        })
        return {
            'name': "Fans",
            'type': 'ir.actions.act_window',
            'res_model': 'organisation.fans',
            'view_mode': 'form',
            'res_id': fan.id,
            'target': 'main',
        }

    # compute methods
    @api.depends('partner_id')
    def _compute_organisation_ids(self):
        for athlete in self:
            organisations = self.env['organisation.organisation'].search(
                [('athlete_ids', 'in', athlete.id)])
            athlete.organisation_ids = organisations

    @api.depends('partner_id')
    def _compute_group_ids(self):
        for athlete in self:
            groups = self.env['athlete.groups'].search(
                [('athlete_ids', 'in', athlete.id)])
            athlete.group_ids = groups

    @api.depends('dob')
    def _compute_age(self):
        # Get the current date
        today = fields.Date.today()
        for rec in self:
            rec.age = 0
            if rec.dob:
                # Get the difference between the current date and the birthday
                age = relativedelta(today, rec.dob)
                rec.age = age.years

    @api.depends('partner_id')
    def _compute_invoices(self):
        for athlete in self:
            athlete.invoice_ids = athlete.partner_id.invoice_ids

    @api.depends('partner_id')
    def _compute_disciplines(self):
        for athlete in self:
            disciplines = self.env['organisation.discipline'].search(
                [('athlete_ids', 'in', athlete.id)])
            athlete.discipline_ids = disciplines

    @api.depends('partner_id')
    def _compute_products(self):
        for athlete in self:
            sale_orders = athlete.partner_id.sale_ids
            order_lines = sale_orders.order_line
            athlete.product_ids = order_lines.product_id

    @api.depends('partner_id')
    def _compute_tasks(self):
        for athlete in self:
            tasks = self.env['project.task'].search(
                [('assign_athlete_ids', 'in', athlete.id), ('task_checkbox', '=', True)])
            athlete.task_ids = tasks

    @api.depends('partner_id')
    def _compute_events(self):
        for athlete in self:
            events = self.env['calendar.event'].search(
                [('partner_ids', 'in', athlete.partner_id.id)])
            athlete.event_ids = events

    @api.depends('partner_id')
    def _compute_parent_ids(self):
        for athlete in self:
            parents = self.env['organisation.parents'].search(
                [('athlete_ids', 'in', athlete.id)])
            athlete.parent_ids = parents

    def _compute_coach_ids(self):
        for athlete in self:
            coaches = self.env['organisation.coaches'].search(
                [('athlete_ids', 'in', athlete.id)])
            athlete.coach_ids = coaches

    @api.depends('partner_id')
    def _compute_vehicle_ids(self):
        for athlete in self:
            vehicles = self.env['vehicle.registration'].search(
                [('athlete_ids', 'in', athlete.id)])
            athlete.vehicle_ids = vehicles

    def _compute_conf_create_fan(self):
        params = self.env['ir.config_parameter'].sudo()
        create_fan = params.get_param('organisation.fan_from_athlete')
        for rec in self:
            rec.conf_create_fan = create_fan



class AthletesTags(models.Model):
    """model for managing athletes tags"""
    _name = "athletes.tags"
    _description = "Athletes Tags"
    _rec_name = 'name'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True)
    color = fields.Integer(string='Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!")]


class AthletesDocuments(models.Model):
    """model for managing athletes documents"""
    _name = "athletes.documents"
    _description = "Athletes Documents"
    _rec_name = 'name'

    name = fields.Char(string="Document Name", required=True)
    description = fields.Text(string="Description", required=True)
    athlete_id = fields.Many2one('organisation.athletes')
    group_id = fields.Many2one('athlete.groups')
    coach_id = fields.Many2one('organisation.coaches', string="Coach")
    document = fields.Binary(string="Document", required=False)
    document_id = fields.Many2one('ir.attachment')
    company_id = fields.Many2one('res.company', required=True)
    organisation_ids = fields.Many2many('organisation.organisation', store=True,
                                        readonly=False, string="Organisation",)

    # create
    @api.model
    def create(self, vals):
        """create methode"""

        result = super(AthletesDocuments, self).create(vals)
        print(vals, "vals")

        return result


