# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProjectScrumRole(models.Model):
    _name = 'project.scrum.role'
    _description = 'Project Scrum Role'

    name = fields.Char('Name',required=True)
    code = fields.Char('Code')
    project_id = fields.Many2one('project.project', "Project")
    person_name = fields.Char('Person Name')
    person_description = fields.Text('Person Description')
