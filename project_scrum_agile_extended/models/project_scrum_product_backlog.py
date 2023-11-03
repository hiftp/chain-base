# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class ProjectScrumProductBacklog(models.Model):
    _inherit = "project.scrum.product.backlog"

    @api.depends(
        "tasks_id",
        "tasks_id.estimate_adjustment",
        "tasks_id.effective_hours",
        "tasks_id.planned_hours",
        "tasks_id.progress",
        "tasks_id.stage_id",
        "tasks_id.product_backlog_id.task_hours",
        "sprint_id",
        "sprint_id.expected_hours",
    )
    def _compute_hours(self):
        """ This method is used to calculate weightage  based in related task
            estimate hours, effective hours, planned hours, progress,
            weightage etc """
        stage_id = self.env["project.task.type"].search(
            [("name", "ilike", "Cancel")], limit=1
        )
        for backlog in self:
            effective = task_hours = progress = 0.0
            for task in backlog.tasks_id.filtered(
                lambda t: t.stage_id.id != stage_id.id
            ):
                task_hours += task.planned_hours + task.estimate_adjustment
                effective += task.effective_hours

                # if backlog.expected_hours > 0 and task.planned_hours > 0:
                # old Formula
                # progress += (task.progress * (
                #     task.planned_hours + task.estimate_adjustment) / backlog.expected_hours)

            # if len(backlog.tasks_id.ids) > 0:
            #     progress = round(progress / len(backlog.tasks_id.ids))

            backlog.effective_hours = effective
            backlog.task_hours = task_hours

            # New Formula for progress in version 2
            # Not add below code in above for loop because calculation not work
            # proper if we add in above task loop
            for task in backlog.tasks_id.filtered(
                lambda t: t.stage_id.id != stage_id.id
            ):
                # progress += (task.weightage * task.progress)
                hours = task.planned_hours + task.estimate_adjustment
                if task.product_backlog_id.task_hours > 0:
                    progress += (
                        hours / task.product_backlog_id.task_hours
                    ) * task.progress

            backlog.progress = progress
            backlog.weightage = (
                backlog.expected_hours / backlog.sprint_id.expected_hours
                if backlog.sprint_id and backlog.sprint_id.expected_hours > 0
                else 0
            )

    def _compute_author_id_editable(self):
        """" This method is used to define author is editable or not
            based on group and state """
        grp_pm = self.env.user.has_group("project_management_security.group_im")
        grp_custom_prj_crd = self.env.user.has_group(
            "project_management_security.group_project_coordinator"
        )
        for record in self:
            record.author_id_editable = (
                True
                if (
                    grp_pm
                    or grp_custom_prj_crd
                    or record.project_id.user_id.id == self.env.user.id
                    or record.state == "draft"
                )
                else False
            )

    name = fields.Char(
        "Title",
        required=True,
        translate=True,
        size=128,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    for_then = fields.Text(
        "For",
        translate=True,
        readonly=True,
        size=128,
        states={"draft": [("readonly", False)]},
    )
    backlog_number = fields.Char(
        "Number Requirement",
        readonly=True,
        copy=False,
        size=150,
        help="Sequence number of request",
    )
    weightage = fields.Float(compute="_compute_hours",compute_sudo=True)
    author_id_editable = fields.Boolean(
        "Author Editable", compute="_compute_author_id_editable", store=False
    )

    def _valid_field_parameter(self, field, name):
        return name == 'size' or super()._valid_field_parameter(field, name)

    def write(self, vals):
        """ This method is used to update logs of backlog details in release
            based on release detail update which used in backlog """
        if vals.get("release_id", ""):
            user_name = self.env.user.name
            for rec in self:
                if rec.release_id:
                    msg = (
                        _(
                            """ <ul class="o_mail_thread_message_tracking">
                        <li>Backlog Removed by: <span> %s </span></li><li>
                        Backlog Number: <span> %s </span></li>
                        Backlog Name: <span> %s </span></li>"""
                        )
                        % (user_name, rec.backlog_number, rec.name)
                    )
                    rec.release_id.message_post(body=msg)
        res = super(ProjectScrumProductBacklog, self).write(vals)
        if vals.get("release_id", ""):
            user_name = self.env.user.name
            for rec in self:
                if rec.release_id:
                    msg = (
                        _(
                            """ <ul class="o_mail_thread_message_tracking">
                        <li>Backlog Added by: <span> %s </span></li><li>
                        Backlog Number: <span> %s </span></li>
                        Backlog Name: <span> %s </span></li>"""
                        )
                        % (user_name, rec.backlog_number, rec.name)
                    )
                    rec.release_id.message_post(body=msg)
        return res

    @api.model_create_multi
    def create(self, vals_lst):
        """ This method is used to manage logs of backlog details in release
            based on release used """
        result = super(ProjectScrumProductBacklog, self).create(vals_lst)
        user_name = self.env.user.name
        for rec in result:
            if rec.project_id.user_id:
                rec.message_unsubscribe(partner_ids=[rec.project_id.user_id.id])
            if rec.release_id:
                msg = (
                    _(
                        """ <ul class="o_mail_thread_message_tracking">
                    <li>Backlog Added by: <span> %s </span></li><li>
                    Backlog Number: <span> %s </span></li>
                    Backlog Name: <span> %s </span></li>"""
                    )
                    % (user_name, rec.backlog_number, rec.name)
                )
                rec.release_id.message_post(body=msg)
        return result

    def unlink(self):
        """ This method is used to remove logs from release detail when
            release removed form the backlog """
        user_name = self.env.user.name
        for rec in self:
            if rec.release_id:
                msg = (
                    _(
                        """ <ul class="o_mail_thread_message_tracking">
                    <li>Backlog Removed by: <span> %s </span></li><li>
                    Backlog Number: <span> %s </span></li>
                    Backlog Name: <span> %s </span></li>"""
                    )
                    % (user_name, rec.backlog_number, rec.name)
                )
                rec.release_id.message_post(body=msg)
        return super(ProjectScrumProductBacklog, self).unlink()
