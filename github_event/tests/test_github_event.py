# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ddt import ddt, data, unpack
from .common import GithubEventCase


@ddt
class TestGithubEvent(GithubEventCase):

    @data(
        ('pull_request_1_merged.json', 'closed'),
        ('pull_request_2_closed.json', 'closed'),
        ('pull_request_2_reopened.json', 'reopened'),
        ('check_run_completed.json', 'completed'),
    )
    @unpack
    def test_action(self, filename, expected_action):
        self.event_1.payload = self._read_payload(filename)
        self.event_1.process()
        assert self.event_1.action == expected_action
