# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProjectScrumRelease(models.Model):
    _name = 'project.scrum.release'
    _description = 'Project Release'
    _inherit = ['mail.thread']
    _order = "release_number desc"

    name = fields.Char("Name", required=True)
    goal = fields.Text("Goal")
    note = fields.Text("Note")
    project_id = fields.Many2one('project.project', "Project",
                                 domain=[('is_scrum', '=', True)])
    date_start = fields.Date('Starting Date')
    date_stop = fields.Date('Ending Date')
    delivery_date_estimated = fields.Date("Estimated Date of Delivery")
    delivery_date_effective = fields.Date("Effective Date of Delivery")
    sprint_ids = fields.One2many(
        'project.scrum.sprint',
        'release_id',
        "Sprints"
    )
    backlog_ids = fields.One2many(
        'project.scrum.product.backlog',
        'release_id',
        "Product Backlog",
        readonly=True
    )
    release_number = fields.Char(
        'Release Number',
        copy=False,
        help="Sequence of the release number"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('release_number'):
                vals['release_number'] = \
                    self.env['ir.sequence'].next_by_code('project.scrum.release') \
                    or '/'
        return super(ProjectScrumRelease, self).create(vals_list)

    @api.constrains('date_start', 'date_stop')
    def _check_dates(self):
        for scrum in self:
            if (scrum.date_start and scrum.date_stop) and (
                    scrum.date_start > scrum.date_stop):
                raise ValidationError(_(
                    'The start date must be anterior to the end date !'))
