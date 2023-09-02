# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class GithubPullRequestTask(models.Model):

    _inherit = "github.pull_request"

    task_ids = fields.Many2many(
        'project.task',
        'pull_request_task_ref',
        'pull_request_id',
        'task_id',
        string='Tasks'
    )

    @api.model
    def create(self, vals):
        pr = super().create(vals)
        pr.task_ids._update_pull_request_tags()
        return pr

    def write(self, vals):
        must_update_tags_on_tasks = 'task_ids' in vals or 'state' in vals

        if must_update_tags_on_tasks:
            tasks_to_update = self.mapped('task_ids')

        super().write(vals)

        if must_update_tags_on_tasks:
            tasks_to_update |= self.mapped('task_ids')
            tasks_to_update._update_pull_request_tags()

        return True


def has_pull_request_at_state(task: 'project.task', state: str) -> bool:
    """Return True if the task has at least one PR at the given state."""
    return task.pull_request_ids.filtered(lambda pr: pr.state == state)


class ProjectTaskPullRequest(models.Model):

    _inherit = "project.task"

    pull_request_ids = fields.Many2many(
        'github.pull_request',
        'pull_request_task_ref',
        'task_id',
        'pull_request_id',
        string='Pull Requests',
        copy=False,
    )

    def _compute_pull_request_qty(self):
        for record in self:
            record.pull_request_qty = len(record.pull_request_ids)

    pull_request_qty = fields.Integer(compute="_compute_pull_request_qty")

    def _check_all_pull_request_state(self):
        for record in self:
            record.no_pull_request_open = is_no_pull_request_open(record)

    @api.model
    def create(self, vals):
        task = super().create(vals)
        task._update_pull_request_tags()
        return task

    def write(self, vals):
        super().write(vals)

        if 'pull_request_ids' in vals:
            self._update_pull_request_tags()

        return True

    def _update_pull_request_tags(self):
        tag_open = self.env.ref(
            'github_pull_request_project.tag_pull_request_open')
        tag_merged = self.env.ref(
            'github_pull_request_project.tag_pull_request_merged')
        tag_closed = self.env.ref(
            'github_pull_request_project.tag_pull_request_closed')

        for task in self:
            show_open_tag = (
                has_pull_request_at_state(task, 'open')
            )
            show_merged_tag = (
                has_pull_request_at_state(task, 'merged') and
                not show_open_tag
            )
            show_closed_tag = (
                has_pull_request_at_state(task, 'closed') and
                not show_open_tag and
                not show_merged_tag
            )

            task.update({'tag_ids': [
                (4 if show_open_tag else 3, tag_open.id),
                (4 if show_merged_tag else 3, tag_merged.id),
                (4 if show_closed_tag else 3, tag_closed.id),
            ]})

    @api.onchange('pull_request_ids')
    def _onchange_pull_requests_update_tags(self):
        self._update_pull_request_tags()
