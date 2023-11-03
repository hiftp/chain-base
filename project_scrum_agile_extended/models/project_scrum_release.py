# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class ProjectScrumRelease(models.Model):
    _inherit = "project.scrum.release"

    @api.depends(
        "total_planned_hours",
        "total_planned_hours_edit",
        "sprint_ids",
        "sprint_ids.progress",
        "sprint_ids.expected_hours",
        "sprint_ids.state",
    )
    def _compute_progress(self):
        """ This method used to calculate progress based on planned hours,
            sprint progress, sprint expected hours etc """
        for release in self:
            total_planned_hours = release.total_planned_hours
            if not release.sprint_ids:
                total_planned_hours = release.total_planned_hours_edit
            release.progress = sum(
                sprint.progress * sprint.expected_hours / total_planned_hours
                for sprint in release.sprint_ids
                if sprint.state != "cancel" and sprint.expected_hours > 0
            )

    @api.depends("sprint_ids", "sprint_ids.expected_hours", "sprint_ids.state")
    def _compute_hours(self):
        """ This method used to calculate milestone planned hours based on
            sprint details and sprint detail's expected hours """
        for release in self:
            release.total_planned_hours = sum(
                sprint.expected_hours
                for sprint in release.sprint_ids
                if sprint.state != "cancel"
            )

    @api.depends("total_planned_hours",
                 "total_planned_hours_edit",
                 "project_id",
                 "project_id.release_ids",
                 "project_id.release_ids.sprint_ids",
                 "project_id.release_ids.total_planned_hours_edit",
                 "project_id.release_ids.total_planned_hours",
                 )
    def _compute_weightage(self):
        """ This method used to calculate weightage of release based on
            milestone planned hours """
        for release in self:
            total_m_h = 0
            weightage = 0
            for rel in release.project_id.release_ids:
                if not rel.sprint_ids:
                    total_m_h += rel.total_planned_hours_edit
                else:
                    total_m_h += rel.total_planned_hours

            if not release.sprint_ids:
                if release.total_planned_hours_edit > 0 and total_m_h > 0:
                    weightage = release.total_planned_hours_edit / total_m_h
            else:
                if release.total_planned_hours > 0 and total_m_h > 0:
                    weightage = release.total_planned_hours / total_m_h
            release.weightage = weightage

    name = fields.Char("Name", required=True, size=128)
    release_number = fields.Char(
        "Release Number", copy=False, size=150, help="Sequence of the release number"
    )
    progress = fields.Float(
        compute="_compute_progress",
        string="Progress (0-100)",
        help="Computed as avg. progress of related sprints",
    )
    total_planned_hours = fields.Float(
        compute="_compute_hours",
        string="Milestone Planned Hour",
        help="Estimated time to do the sprints.",
    )
    total_planned_hours_edit = fields.Float(
        string="Milestone Planned Hours", help="Estimated time to do the sprints.",
    )
    weightage = fields.Float(compute="_compute_weightage")

    def _valid_field_parameter(self, field, name):
        return name == 'size' or super()._valid_field_parameter(field, name)

    @api.model_create_multi
    def create(self, vals_lst):
        """ This method used to manage release details log in
            project used in release """
        result = super(ProjectScrumRelease, self).create(vals_lst)
        user_name = self.env.user.name
        for rec in result:
            if rec.project_id:
                msg = (
                    _(
                        """ <ul class="o_mail_thread_message_tracking">
                    <li>Release Added by: <span> %s </span></li><li>
                    Release Number: <span> %s </span></li>
                    Release Name: <span> %s </span></li>"""
                    )
                    % (user_name, rec.release_number, rec.name)
                )
                rec.project_id.message_post(body=msg)
        return result

    def write(self, vals):
        """ This method used to update release details in project
            used in release """
        if vals.get("project_id", ""):
            user_name = self.env.user.name
            for rec in self:
                if rec.project_id:
                    msg = (
                        _(
                            """ <ul class="o_mail_thread_message_tracking">
                        <li>Release Removed by: <span> %s </span></li><li>
                        Release Number: <span> %s </span></li>
                        Release Name: <span> %s </span></li>"""
                        )
                        % (user_name, rec.release_number, rec.name)
                    )
                    rec.project_id.message_post(body=msg)
        res = super(ProjectScrumRelease, self).write(vals)
        if vals.get("project_id", ""):
            user_name = self.env.user.name
            for rec in self:
                if rec.project_id:
                    msg = (
                        _(
                            """ <ul class="o_mail_thread_message_tracking">
                        <li>Release Added by: <span> %s </span></li><li>
                        Release Number: <span> %s </span></li>
                        Release Name: <span> %s </span></li>"""
                        )
                        % (user_name, rec.release_number, rec.name)
                    )
                    rec.project_id.message_post(body=msg)
        return res
