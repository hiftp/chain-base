# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import re
from odoo import fields, models, api
from .common import PULL_REQUEST_STATES, OPEN


regex_github_source = re.compile(
    r'https:\/\/(?P<host>[\w\.]+)/'
    r'(?P<organization>\w+)/'
    r'(?P<repository>[\w\-_]+)/'
    r'pull/'
    r'(?P<pull_request_number>\d+)'
)


class GithubPullRequest(models.Model):
    _name = "github.pull_request"
    _description = "Github Pull Request"
    _rec_name = 'title'

    title = fields.Char()
    source = fields.Char(required=True)
    state = fields.Selection(
        PULL_REQUEST_STATES,
        default=OPEN,
    )
    developer_id = fields.Many2one(
        'res.partner', 'Developer', ondelete='restrict', index=True)
    host = fields.Char(readonly=True)
    organization = fields.Char(readonly=True)
    repository = fields.Char(readonly=True)
    pull_request_number = fields.Integer(readony=True)

    _sql_constraints = [
        ('source', 'UNIQUE (source)', 'A Pull Request already exists for this source'),
    ]

    @api.model
    def create(self, vals):
        updated_vals = update_according_to_source(vals['source'], vals)
        return super().create(updated_vals)

    def write(self, vals):
        updated_vals = update_according_to_source(vals.get('source', ''), vals)
        super().write(updated_vals)


def update_according_to_source(source: str, vals: dict) -> dict:
    res = re.match(regex_github_source, source)
    if res:
        vals.update(res.groupdict())
    return vals


class GithubPullRequestWithEvents(models.Model):

    _inherit = 'github.pull_request'

    latest_update = fields.Datetime()
    event_ids = fields.One2many(
        'github.event', 'pull_request_id', 'Events',
    )

    def is_latest_event(self, event):
        """Verify whether an event is the latest event recorded for this pull request.

        :ptype event: github.event
        :rtype: bool
        """
        return not self.latest_update or event.pull_request_updated_at >= self.latest_update

    def update_from_event(self, event):
        """Update the pull request from the given event.

        :ptype event: github.event
        """
        self.state = event.pull_request_state
        self.latest_update = event.pull_request_updated_at
        self.title = event.pull_request_title
