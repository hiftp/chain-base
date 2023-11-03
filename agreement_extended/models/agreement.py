# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class Agreement(models.Model):
    _inherit = "agreement"

    project_ids = fields.Many2many("project.project", string="Projects")
    description = fields.Text("Description")
    state = fields.Selection(
        [
            ("active", "Active"),
            ("closed", "Closed"),
            ("expired", "Expired"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        required=True,
        copy=False,
        default="active",
        tracking=True,
    )
