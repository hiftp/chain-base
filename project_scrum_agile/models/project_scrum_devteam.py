# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProjectScrumDevteam(models.Model):
    _name = 'project.scrum.devteam'
    _description = "Project Scrum Development Team"

    name = fields.Char("Name", required=True)
    code = fields.Char("Code")
    active = fields.Boolean("Active", default=True)
    developer_ids = fields.One2many(
        'res.users',
        'scrum_devteam_id',
        "Developers"
    )


class ResUsers(models.Model):
    _inherit = "res.users"

    scrum_devteam_id = fields.Many2one(
        'project.scrum.devteam',
        "Scrum Development Team"
    )
