# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.tests import common


class TestProjectTask(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pull_request_open = cls.env["github.pull_request"].create({
            "source": "https://github.com/Numigi/odoo-git-addons/pull/1",
            "state": "open"
        })
        cls.pull_request_closed = cls.env["github.pull_request"].create({
            "source": "https://github.com/Numigi/odoo-git-addons/pull/2",
            "state": "closed"
        })
        cls.pull_request_merged = cls.env["github.pull_request"].create({
            "source": "https://github.com/Numigi/odoo-git-addons/pull/3",
            "state": "merged"
        })

        cls.tag_open = cls.env.ref(
            'github_pull_request_project.tag_pull_request_open')
        cls.tag_merged = cls.env.ref(
            'github_pull_request_project.tag_pull_request_merged')
        cls.tag_closed = cls.env.ref(
            'github_pull_request_project.tag_pull_request_closed')

    # Simple cases
    def test_whenNoPR_thenNoTag(self):
        task = self.env["project.task"].create({
            "name": "ttask", "pull_request_ids": [(5, False, False)]
        })
        assert not task.tag_ids

    def test_whenPrAreMerged_thenTaskMerged(self):
        task = self.env["project.task"].create({
            "name": "ttask", "pull_request_ids": [(6, False, (self.pull_request_merged.id,))]
        })
        assert task.tag_ids == self.tag_merged

    def test_whenPrAreClosed_thenTaskClosed(self):
        task = self.env["project.task"].create({
            "name": "ttask", "pull_request_ids": [(6, False, (self.pull_request_closed.id,))]
        })
        assert task.tag_ids == self.tag_closed

    def test_whenPrAreOpen_thenTaskOpen(self):
        task = self.env["project.task"].create({
            "name": "ttask", "pull_request_ids": [(6, False, (self.pull_request_open.id,))]
        })
        assert task.tag_ids == self.tag_open

    # Mixing cases
    def test_whenAllStates_thenTaskOpen(self):
        task = self.env["project.task"].create({
            "name": "ttask",
            "pull_request_ids": [(
                6, False,
                (
                    self.pull_request_open.id,
                    self.pull_request_closed.id,
                    self.pull_request_merged.id
                )
            )]
        })
        assert task.tag_ids == self.tag_open

    def test_whenClosedAndMerged_thenTaskMerged(self):
        task = self.env["project.task"].create({
            "name": "ttask",
            "pull_request_ids": [(
                6, False, (self.pull_request_closed.id,
                           self.pull_request_merged.id)
            )]
        })
        assert task.tag_ids == self.tag_merged

    def test_whenMergedAndOpen_thenTaskOpen(self):
        task = self.env["project.task"].create({
            "name": "ttask",
            "pull_request_ids": [(
                6, False, (self.pull_request_merged.id,
                           self.pull_request_open.id)
            )]
        })
        assert task.tag_ids == self.tag_open

    def test_whenClosedAndOpen_thenTaskOpen(self):
        task = self.env["project.task"].create({
            "name": "ttask",
            "pull_request_ids": [(
                6, False, (self.pull_request_closed.id,
                           self.pull_request_open.id)
            )]
        })
        assert task.tag_ids == self.tag_open

    def test_onTaskWrite_tagsUpdated(self):
        task = self.env["project.task"].create({
            "name": "ttask",
        })
        task.pull_request_ids = self.pull_request_open
        assert task.tag_ids == self.tag_open

    def test_onPullRequestStateChange_tagsUpdated(self):
        task = self.env["project.task"].create({
            "name": "ttask",
            "pull_request_ids": [(4, self.pull_request_open.id)],
        })
        assert task.tag_ids == self.tag_open
        self.pull_request_open.state = 'merged'
        assert task.tag_ids == self.tag_merged

    def test_onPullRequestTaskIdsChange_tagsUpdated(self):
        task = self.env["project.task"].create({
            "name": "ttask",
        })
        self.pull_request_open.task_ids = task
        assert task.tag_ids == self.tag_open

    def test_onPullRequestCreate_tagsUpdated(self):
        task = self.env["project.task"].create({
            "name": "ttask",
        })
        self.env["github.pull_request"].create({
            "source": "https://github.com/Numigi/odoo-git-addons/pull/999",
            "state": "open",
            "task_ids": [(4, task.id)],
        })
        assert task.tag_ids == self.tag_open
