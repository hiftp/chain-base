# -*- coding: utf-8 -*-
"""Parents"""


from odoo import fields, models, api
from random import randint
from odoo.tools import email_normalize


class Parents(models.Model):
    """model for managing Parents"""
    _name = "organisation.parents"
    _description = "Parents"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, related='partner_id.name')
    active = fields.Boolean('Active', default=True)
    img_parents = fields.Image()
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
    date = fields.Date(string="Date", default=fields.Date.today())
    organisation_ids = fields.Many2many('organisation.organisation', store=True,
                                        compute='_compute_organisation_ids',
                                        readonly=False, string="Organisation",
                                        domain=[('has_parents', '=', True)])
    responsible_user_id = fields.Many2one('res.users', string="Responsible",
                                          tracking=True)
    tag_ids = fields.Many2many('parents.tags', string="Tags")
    athlete_ids = fields.Many2many('organisation.athletes',
                                   string="Athletes", readonly=False, store=True,
                                   compute='_compute_athlete_ids')
    invoice_ids = fields.Many2many('account.move', 'parent_invoice_rel',
                                   'parent_id', 'invoice_id',
                                   string="Invoices",
                                   compute='_compute_invoices')
    create_booking = fields.Boolean("Booking creation",
                                    related='partner_id.create_booking')

    subscription_count = fields.Integer()

    _sql_constraints = [
        ('partner_uniq', 'unique (partner_id)', "You cannot create "
                                                "Parents with same contact!")]

    # create
    @api.model
    def create(self, vals):
        """create methode"""
        result = super(Parents, self).create(vals)
        result.partner_id.write({'org_group_selection': 'parents'})
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
                        'organisation.group_organisation_parents').id,
                            self.env.ref('base.group_portal').id])]
            })
        return result

    # unlink
    def unlink(self):
        partner = self.partner_id
        partner.org_group_selection = False
        partner.create_booking = False
        return super(Parents, self).unlink()

    # compute methods
    @api.depends('partner_id')
    def _compute_invoices(self):
        for parent in self:
            parent.invoice_ids = parent.partner_id.invoice_ids

    @api.depends('partner_id')
    def _compute_organisation_ids(self):
        for parent in self:
            organisations = self.env['organisation.organisation'].search(
                [('parent_ids', 'in', parent.id)])
            parent.organisation_ids = organisations

    @api.depends('partner_id')
    def _compute_athlete_ids(self):
        for parent in self:
            athletes = self.env['organisation.athletes'].search(
                [('parent_ids', 'in', parent.id)])
            parent.athlete_ids = athletes

    def action_subscription(self):
        print("self", self)

class ParentsTags(models.Model):
    """model for managing parents tags"""
    _name = "parents.tags"
    _description = "Parents Tags"
    _rec_name = 'name'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True)
    color = fields.Integer(string='Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!")]
