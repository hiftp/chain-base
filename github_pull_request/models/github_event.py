# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import dateutil.parser
from odoo import fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from .common import PULL_REQUEST_STATES, MERGED


class GithubEvent(models.Model):

    _inherit = 'github.event'

    pull_request_id = fields.Many2one(
        'github.pull_request',
        'Pull Request',
        ondelete='restrict',
        index=True,
        copy=False,
    )
    pull_request_updated_at = fields.Datetime()
    pull_request_title = fields.Char()
    pull_request_state = fields.Selection(
        PULL_REQUEST_STATES,
    )

    def _find_existing_pull_request(self, url):
        return self.env['github.pull_request'].search([
            ('source', '=', url),
        ])

    def _make_pull_request(self, url):
        return self.env['github.pull_request'].create({'source': url})

    def _get_pull_request(self):
        url = self._get_value_from_payload('pull_request.html_url')
        existing_pull_request = self._find_existing_pull_request(url)
        return existing_pull_request or self._make_pull_request(url)

    def _get_pull_request_state(self):
        is_merged = self._get_value_from_payload('pull_request.merged_at')
        return MERGED if is_merged else self._get_value_from_payload('pull_request.state')

    def _get_pull_request_updated_at(self):
        datetime_string = self._get_value_from_payload(
            'pull_request.updated_at')
        datetime_obj = dateutil.parser.parse(datetime_string)
        naive_datetime_string = datetime_obj.strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        return naive_datetime_string

    def _get_pull_request_title(self):
        return self._get_value_from_payload("pull_request.title")

    def _update_from_pull_request_fields(self):
        """Update the event's data related to pull requests from its payload."""
        self.write({
            'pull_request_id': self._get_pull_request().id,
            'pull_request_state': self._get_pull_request_state(),
            'pull_request_updated_at': self._get_pull_request_updated_at(),
            'pull_request_title': self._get_pull_request_title(),
        })

    def process(self):
        super().process()

        is_pull_request_event = 'pull_request' in self.payload_serialized
        if is_pull_request_event:
            self._update_from_pull_request_fields()

            if self.pull_request_id.is_latest_event(self):
                self.pull_request_id.update_from_event(self)
