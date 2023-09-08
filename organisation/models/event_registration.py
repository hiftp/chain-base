from odoo import models, api, fields, _


class EventRegistration(models.Model):
    _inherit = 'event.registration'


    def action_create_athlete(self):
        """ Open the athlete.creation wizard to create athlete.
                :return: An action opening the athlete.creation wizard.
                """
        print(self.env.context)
        if self.env.context.get('params') and self.env.context['params'].get('model') == 'event.registration':
            attendee_id = self.env['event.registration'].browse(
                        self.env.context['params'].get('id'))

            partner = self.env['res.partner'].create({
                        'name': attendee_id.name,
                        'email': attendee_id.email,
                        'phone': attendee_id.phone,
                        'org_group_selection': 'athletes'
                    })
            if attendee_id.parent_name:
                parent_partner = self.env['res.partner'].create({
                            'name': attendee_id.parent_name,
                            'email': attendee_id.parent_email,
                            'phone': attendee_id.parent_phone,
                            'org_group_selection': 'parents'
                        })
                parent = self.env['organisation.parents'].create({
                    'partner_id': parent_partner.id
                })
            if partner:
                view = self.env.ref('organisation.view_create_athlete')
                # if not self.email:
                #     raise ValidationError(_(
                #         "Your selected contact does not contains a valid email "
                #         "\n Please provide email address."))
                return {
                    'name': _('Create Athlete'),
                    'res_model': 'athlete.creation',
                    'view_mode': 'form',
                    'context': {
                        'active_model': 'res.partner',
                        'active_id': self.id,
                        'partner_id': partner.id,
                        'parent_ids': parent.id
                    },
                    'view_id': view.id,
                    'target': 'new',
                    'type': 'ir.actions.act_window',
                }

    # def action_create_parent(self):
    #     """ Open the parent.creation wizard to create parent.
    #             :return: An action opening the parent.creation wizard.
    #             """
    #     # if not self.email:
    #     #     raise ValidationError(_(
    #     #         "Your selected contact does not contains a valid email "
    #     #         "\n Please provide email address."))
    #     return {
    #         'name': _('Create Parent'),
    #         'res_model': 'parent.creation',
    #         'view_mode': 'form',
    #         'context': {
    #             'active_model': 'res.partner',
    #             'active_id': self.id,
    #             'partner_id': self.id,
    #         },
    #         'target': 'new',
    #         'type': 'ir.actions.act_window',
    #     }

    # def action_create_athlete(self):
    #     print("hiiiii", self.env.context)
    #     if self.env.context['params'].get('model') == 'event.registration':
    #         attendee_id = self.env['event.registration'].browse(
    #             self.env.context['params'].get('id'))
    #         print(attendee_id)
    #         partner = self.env['res.partner'].create({
    #             'name': attendee_id.name,
    #             'email': attendee_id.email,
    #             'phone': attendee_id.phone
    #         })
    #         athlete_id = self.env['organisation.athletes'].create({
    #             'partner_id': partner.id,
    #
    #         })