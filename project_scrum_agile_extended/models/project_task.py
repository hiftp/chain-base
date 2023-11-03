# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.depends(
        "timesheet_ids",
        "timesheet_ids.unit_amount",
        "estimate_adjustment",
        "planned_hours",
        "child_ids",
        "child_ids.planned_hours",
        "child_ids.effective_hours",
        "child_ids.subtask_effective_hours",
        "child_ids.stage_id",
        "child_ids.stage_id.fold",
        "product_backlog_id.task_hours",
    )
    def _compute_hours_get(self):
        """ This method is used to calculate weightage based on task stage,
            timesheet amount, estimate adjustment, planned hours,
            child task planned hours, backlog task hours,
            child task effective hours etc """
        for task in self:
            weightage = children_hours = 0
            for child_task in task.child_ids:
                if child_task.stage_id and child_task.stage_id.fold:
                    children_hours += (
                        child_task.effective_hours + child_task.subtask_effective_hours
                    )
                else:
                    children_hours += max(
                        child_task.planned_hours,
                        child_task.effective_hours + child_task.subtask_effective_hours,
                    )

            task.subtask_effective_hours = children_hours
            task.effective_hours = sum(task.sudo().timesheet_ids.mapped("unit_amount"))
            task.remaining_hours = (
                task.planned_hours - task.effective_hours - task.subtask_effective_hours
            )
            # Commented this line as total hours replaced as total hours spent in v15
            # here both line added total hours and total hours spent
            #             task.total_hours = max(task.planned_hours, task.effective_hours)
            task.total_hours_spent = task.effective_hours + task.subtask_effective_hours
            #             task.delay_hours = max(-task.remaining_hours, 0.0)

            story_estimated_hours = task.product_backlog_id.expected_hours
            planned_hours = task.planned_hours
            estimate_adjustment = task.estimate_adjustment

            if story_estimated_hours > 0.0:
                weightage = planned_hours / story_estimated_hours
            hours = planned_hours + estimate_adjustment
            # hours = hours if hours > 0 else 1
            task.weightage = weightage

            if task.product_backlog_id.task_hours > 0:
                # New weightage calculation in Version 2
                task.weightage = hours / task.product_backlog_id.task_hours

            # New progress calculation in Version 2
            if task.effective_hours and hours > 0:
                task.progress = (task.effective_hours / hours) * 100

    name = fields.Char("Homework", size=256, translate=True)
    email = fields.Char(
        "Send mail",
        size=256,
        help="An email will be sent upon completion and upon validation of the"
        "Task to the following recipients. Separate with comma (,)"
        "each recipient ex: example@email.com, test@email.com",
    )
    task_number = fields.Char(
        "Task Number",
        readonly=True,
        copy=False,
        size=64,
        help="Sequence of the task number",
    )
    estimate_adjustment = fields.Float()
    weightage = fields.Float(compute="_compute_hours_get")
    schedule_date = fields.Datetime(help="Date scheduled for task")

    def _valid_field_parameter(self, field, name):
        return name == 'size' or super()._valid_field_parameter(field, name)

    @api.model_create_multi
    def create(self, vals_lst):
        result = super(ProjectTask, self).create(vals_lst)
        for rec in result:
            if rec.manager_id:
                rec.message_unsubscribe(partner_ids=[rec.manager_id.partner_id.id])
        return result

