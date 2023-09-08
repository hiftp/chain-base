# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class ParentCreation(models.TransientModel):
    _name = 'parent.creation'
    _description = 'Parent Creation'

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

    partner_id = fields.Many2one('res.partner', string="Contact",
                                 readonly=True, default=_get_default_partner)
    partner_ids = fields.Many2many('res.partner', string="Contact",
                                   readonly=True, default=_get_default_partners)
    organisation_ids = fields.Many2many('organisation.organisation',
                                        string="Organisations")
    athlete_ids = fields.Many2many('organisation.athletes', string="Athletes")
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

    def action_create_parent(self):
        if self.partner_id:
            if self.in_portal and not self.partner_id.email:
                raise ValidationError(_(
                    "Your selected contact does not contains a valid email "
                    "\n Please provide email address."))
            parent = self.env['organisation.parents'].create({
                'partner_id': self.partner_id.id,
            })
            parent.organisation_ids = self.organisation_ids
            parent.athlete_ids = self.athlete_ids
            if self.in_portal:
                user_ids = self.env['portal.wizard.user'].create(
                    self._default_user_ids(self.partner_id.id))
                user_ids.action_apply()
            return {
                'name': "Parents",
                'type': 'ir.actions.act_window',
                'res_model': 'organisation.parents',
                'view_mode': 'form',
                'res_id': parent.id,
            }
        elif self.partner_ids:
            for partner in self.partner_ids:
                parent = self.env['organisation.parents'].create({
                    'partner_id': partner.id,
                })
                parent.organisation_ids = self.organisation_ids
                parent.athlete_ids = self.athlete_ids
            parents = self.env['organisation.parents'].search([
                ('partner_id', 'in', self.partner_ids.ids)
            ])
            for partner in self.partner_ids:
                user_ids = self.env['portal.wizard.user'].create(
                    self._default_user_ids(partner.id))
                user_ids.action_apply()
            return {
                'name': "Parents",
                'type': 'ir.actions.act_window',
                'res_model': 'organisation.parents',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', parents.ids)],
                'context': {'create': False},
            }
        else:
            return

