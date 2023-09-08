# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import ValidationError
import string
import random


class AthleteCreation(models.TransientModel):
    _name = 'athlete.creation'
    _description = 'Athlete Creation'

    def _get_default_partner(self):
        partner = self.env['res.partner'].search([
            ('id', '=', self.env.context.get('partner_id'))
        ])
        return partner

    def _get_default_partners(self):
        partners = self.env['res.partner'].search([
            ('id', 'in', self.env.context.get('partner_ids'))
        ])
        return partners

    def _get_default_parent(self):
        parent = self.env['organisation.parents'].browse(self.env.context.get('parent_ids'))
        return parent

    partner_id = fields.Many2one('res.partner', string="Contact",
                                 readonly=True, default=_get_default_partner)
    partner_ids = fields.Many2many('res.partner', string="Contact",
                                   readonly=True, default=_get_default_partners)
    organisation_ids = fields.Many2many('organisation.organisation',
                                        string="Organisations")
    parent_ids = fields.Many2many('organisation.parents', string="Parents", default=_get_default_parent)
    group_ids = fields.Many2many('athlete.groups', string="Groups")
    coach_ids = fields.Many2many('organisation.coaches', string="Coaches")
    in_portal = fields.Boolean(default=False, string="Grant portal access")

    def _default_user_ids(self, partner_id):
        """methode to grant portal access"""
        welcome_message = ""
        contact_ids = set()
        user_changes = []
        partner = self.env['res.partner'].sudo().browse(partner_id)
        contact_partners = partner.child_ids.filtered(lambda p: p.type in ('contact', 'other')) | partner
        wizard_id = self.env['portal.wizard'].create(
            {'welcome_message': welcome_message})
        for contact in contact_partners:
            # make sure that each contact appears at most once in the list
            if contact.id not in contact_ids:
                contact_ids.add(contact.id)
                user_changes.append(({
                    'wizard_id': wizard_id.id,
                    'partner_id': contact.id,
                    'email': contact.email,
                    'in_portal': True,
                }))
        return user_changes

    def action_create_athlete(self):
        if self.partner_id:
            if self.in_portal and not self.partner_id.email:
                raise ValidationError(_(
                    "Your selected contact does not contains a valid email "
                    "\n Please provide email address."))
            pin = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=6))
            athlete = self.env['organisation.athletes'].create({
                'partner_id': self.partner_id.id,
                'member_id': str(pin),
            })
            athlete.organisation_ids = self.organisation_ids
            athlete.parent_ids = self.parent_ids
            athlete.group_ids = self.group_ids
            athlete.coach_ids = self.coach_ids
            self.partner_id.athlete_id = athlete.id
            if self.in_portal:
                user_ids = self.env['portal.wizard.user'].create(
                    self._default_user_ids(self.partner_id.id))
                user_ids.action_apply()
            return {
                'name': "Athletes",
                'type': 'ir.actions.act_window',
                'res_model': 'organisation.athletes',
                'view_mode': 'form',
                'res_id': athlete.id,
            }
        elif self.partner_ids:
            for partner in self.partner_ids:
                pin = ''.join(
                    random.choices(string.ascii_uppercase + string.digits, k=6))
                athlete = self.env['organisation.athletes'].create({
                    'partner_id': partner.id,
                    'member_id': str(pin),
                })
                athlete.organisation_ids = self.organisation_ids
                athlete.parent_ids = self.parent_ids
                athlete.group_ids = self.group_ids
                athlete.coach_ids = self.coach_ids
                partner.athlete_id = athlete.id
            athletes = self.partner_ids.athlete_id
            for partner in self.partner_ids:
                user_ids = self.env['portal.wizard.user'].create(
                    self._default_user_ids(partner.id))
                user_ids.action_apply()
            return {
                'name': "Athletes",
                'type': 'ir.actions.act_window',
                'res_model': 'organisation.athletes',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', athletes.ids)],
                'context': {'create': False},
            }
        else:
            return

