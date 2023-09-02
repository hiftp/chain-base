# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json
from odoo import api, fields, models, _
from odoo.addons.base_sparse_field.models.fields import Serialized
from odoo.exceptions import ValidationError


class GithubEvent(models.Model):

    _name = "github.event"
    _description = "Github Event"
    _order = 'id desc'

    payload = fields.Text()
    payload_serialized = Serialized(
        compute='_compute_payload_serialized'
    )

    @api.depends('payload')
    def _compute_payload_serialized(self):
        events_with_payloads = self.filtered(lambda e: e.payload)
        for event in events_with_payloads:
            event.payload_serialized = json.loads(event.payload)

    action = fields.Char()

    def _get_value_from_payload(self, path):
        """Get a value from the payload.

        :param path: a doted notation of the path to access the value.
        :return: the value contained at the given path.
        """
        section = self.payload_serialized
        keys = path.split('.')

        for key in keys[:-1]:
            if not isinstance(section, dict) or key not in section:
                raise ValidationError(_(
                    "The payload does not contain a value at the path {}."
                ).format(path))

            section = section[key]

        return section[keys[-1]]

    def process(self):
        """Process a github event.

        This method is intended to be inherited by other modules
        to add extra behavior when processing a github event.
        """
        self.action = self._get_value_from_payload('action')
