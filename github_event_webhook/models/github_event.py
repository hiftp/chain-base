# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class GithubEvent(models.Model):

    _inherit = "github.event"

    def process_job(self):
        """Process a github event."""
        self.process()
