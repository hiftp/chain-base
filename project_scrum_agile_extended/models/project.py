# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    @api.depends("percentage_completed")
    def _compute_progress(self):
        """ This method used to calculate project progress based on project
            completed percentage """
        for project in self:
            project.progress = (
                project.percentage_completed if project.percentage_completed else 0
            )

    @api.depends(
        "release_ids",
        "release_ids.progress",
        "release_ids.weightage",
    )
    def _compute_overall_progress(self):
        for project in self:
            project.overall_progress = sum(
                release.weightage * release.progress for release in project.release_ids
            )

    @api.depends("actual_hours", "percentage_completed")
    def _compute_closed_hours(self):
        """
        Compute Closed Hours of Project.
        """
        for project in self:
            project.closed_hours = (
                    project.percentage_completed * project.actual_hours
                ) / 100 if project.actual_hours else 0

    @api.depends("release_ids", "release_ids.total_planned_hours")
    def _compute_hours(self):
        for project in self:
            project.total_planned_hours = sum(
                release.total_planned_hours for release in project.release_ids
            )

    progress = fields.Float(
        compute="_compute_progress",
        string="Overall Progress",
        help="Computed as avg. progress of related sprints",
    )
    actual_hours = fields.Float(copy=False, tracking=True)
    percentage_completed = fields.Float(copy=False, tracking=True)
    overall_progress = fields.Float(compute="_compute_overall_progress", tracking=True,
                                    string="Progress")
    closed_hours = fields.Float(compute="_compute_closed_hours", tracking=True)
    total_planned_hours = fields.Float(
        compute="_compute_hours",
        string="Planned Hours",
        help="Estimated time to do the release.",
        tracking=True,
    )


#    Needed for future scope

#     def action_project_form_view(self):
#         self.ensure_one()
#         action = self.env.ref(
#             'project_management_security.action_project_project_report').read()[0]
#         projects = self.env['project.project'].search([(
#             'name', '=', self.name)])
#         if len(projects) > 1:
#             action['domain'] = [('id', 'in', projects.ids)]
#         elif projects:
#             form_view = [(self.env.ref('project.edit_project').id, 'form')]
#             if 'views' in action:
#                 action['views'] = form_view + [
#                     (state, view)
#                     for state, view in action['views'] if view != 'form']
#             else:
#                 action['views'] = form_view
#             action['res_id'] = projects.id
#         return action


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.onchange("project_id")
    def onchange_project(self):
        """ This method is used to update account based on project detail update """
        for line in self:
            line.account_id = (
                line.project_id.analytic_account_id.id
                if line.project_id and line.project_id.analytic_account_id
                else False
            )
