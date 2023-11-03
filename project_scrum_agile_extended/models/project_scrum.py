# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class ProjectScrumSprint(models.Model):
    _inherit = "project.scrum.sprint"

    @api.depends(
        "product_backlog_ids",
        "product_backlog_ids.expected_hours",
        "product_backlog_ids.effective_hours",
        "product_backlog_ids.stage_id",
        "release_id",
        "release_id.sprint_ids",
        "release_id.sprint_ids.expected_hours",
    )
    def _compute_hours(self):
        """ This method used to calculate sprint weightage based on
            backlog effective hours, backlog expected hours,
            estimate adjustment and sprint state """
        stage_id = self.env["project.task.type"].search(
            [("state", "=", "cancelled")], limit=1
        )
        for sprint in self:
            effective = 0
            expected_hours = 0
            progress = 0
            for backlog in sprint.product_backlog_ids:
                if backlog.stage_id.id != stage_id.id:
                    effective += backlog.effective_hours
                    expected_hours += backlog.expected_hours

            sprint.expected_hours = expected_hours

            total_hours = sum(
                line.expected_hours for line in sprint.release_id.sprint_ids
            )
            total_hours = total_hours if total_hours > 0 else 1

            weightage = sprint.expected_hours / total_hours
            sprint.weightage = weightage
            sprint.effective_hours = effective
            sprint.progress = progress

            if sprint.expected_hours > 0:
                sprint.progress = sum(
                    (backlog.progress * backlog.expected_hours / sprint.expected_hours)
                    for backlog in sprint.with_prefetch().product_backlog_ids
                    if backlog.stage_id.id != stage_id.id
                )

    name = fields.Char("Sprint Name", size=64)
    goal = fields.Char("Goal", size=128)
    sprint_number = fields.Char(
        "Sprint number",
        readonly=True,
        copy=False,
        size=150,
        help="Sprint number sequence",
    )
    estimate_adjustment = fields.Float()
    weightage = fields.Float(compute="_compute_hours")

    def _valid_field_parameter(self, field, name):
        return name == 'size' or super()._valid_field_parameter(field, name)

    @api.model_create_multi
    def create(self, vals_list):
        """ This method used to add sprint details log in related
                    release used in sprint """
        result = super(ProjectScrumSprint, self).create(vals_list)
        user_name = self.env.user.name
        for rec in result:
            if rec.release_id:
                msg = (
                    _(
                        """ <ul class="o_mail_thread_message_tracking">
                    <li>Sprint Added by: <span> %s </span></li><li>
                    Sprint Number: <span> %s </span></li>
                    Sprint Name: <span> %s </span></li>"""
                    )
                    % (user_name, rec.sprint_number, rec.name)
                )
                rec.release_id.message_post(body=msg)
        return result

    def write(self, vals):
        """ This method used to update sprint detail logs in related
            release used in sprint """
        if vals.get("release_id", ""):
            user_name = self.env.user.name
            for rec in self:
                if rec.release_id:
                    msg = (
                        _(
                            """ <ul class="o_mail_thread_message_tracking">
                        <li>Sprint Removed by: <span> %s </span></li><li>
                        Sprint Number: <span> %s </span></li>
                        Sprint Name: <span> %s </span></li>"""
                        )
                        % (user_name, rec.sprint_number, rec.name)
                    )
                    rec.release_id.message_post(body=msg)
        res = super(ProjectScrumSprint, self).write(vals)
        if vals.get("release_id", ""):
            user_name = self.env.user.name
            for rec in self:
                if rec.release_id:
                    msg = (
                        _(
                            """ <ul class="o_mail_thread_message_tracking">
                        <li>Sprint Added by: <span> %s </span></li><li>
                        Sprint Number: <span> %s </span></li>
                        Sprint Name: <span> %s </span></li>"""
                        )
                        % (user_name, rec.sprint_number, rec.name)
                    )
                    rec.release_id.message_post(body=msg)
        return res

    def unlink(self):
        """ This method used to manage logs in sprint when remove
            release from sprint """
        user_name = self.env.user.name
        for rec in self:
            if rec.release_id:
                msg = (
                    _(
                        """ <ul class="o_mail_thread_message_tracking">
                    <li>Sprint Removed by: <span> %s </span></li><li>
                    Sprint Number: <span> %s </span></li>
                    Sprint Name: <span> %s </span></li>"""
                    )
                    % (user_name, rec.sprint_number, rec.name)
                )
                rec.release_id.message_post(body=msg)
        return super(ProjectScrumSprint, self).unlink()
