# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.github_event.tests.common import GithubEventCase
from ddt import ddt, data, unpack


@ddt
class TestGithubEvent(GithubEventCase):

    def test_if_not_pull_request_event__no_pull_request_created(self):
        self.event_1.payload = self._read_payload('check_run_completed.json')
        self.event_1.process()
        assert not self.event_1.pull_request_id

    def test_if_not_existing_pull_request__new_pull_request_created(self):
        self.event_1.payload = self._read_payload(
            'pull_request_2_reopened.json')
        self.event_1.process()
        assert self.event_1.pull_request_id

    def test_if_existing_pull_request__event_attached_to_same_pull_request(self):
        self.event_1.payload = self._read_payload('pull_request_2_closed.json')
        self.event_2.payload = self._read_payload(
            'pull_request_2_reopened.json')
        self.event_1.process()
        self.event_2.process()
        assert self.event_1.pull_request_id
        assert self.event_1.pull_request_id == self.event_2.pull_request_id

    def test_event_can_be_processed_twice(self):
        self.event_1.payload = self._read_payload('pull_request_2_closed.json')
        self.event_1.process()

        initial_pull_request = self.event_1.pull_request_id

        self.event_1.process()
        assert self.event_1.pull_request_id == initial_pull_request

    @data(
        ('pull_request_1_merged.json', 'merged'),
        ('pull_request_2_closed.json', 'closed'),
        ('pull_request_2_reopened.json', 'open'),
    )
    @unpack
    def test_status(self, filename, expected_state):
        self.event_1.payload = self._read_payload(filename)
        self.event_1.process()
        assert self.event_1.pull_request_id.state == expected_state

    @data(
        ('pull_request_2_closed.json', 'pull_request_2_reopened.json'),
        ('pull_request_2_reopened.json', 'pull_request_2_closed.json'),
    )
    @unpack
    def test_if_not_last_event__pull_request_not_updated(self, first_event, second_event):
        """Test that the pull request is only updated by the latest event.

        The event pull_request_closed is updated at: 2023-11-22T17:12:05Z
        The event pull_request_reopened  is updated at: 2023-11-22T17:50:29Z

        The final result is that the pull request is open, because
        the pull request is closed, then reopened.

        This result must not depend on whether one event is processed before the other.
        """
        self.event_1.payload = self._read_payload(first_event)
        self.event_2.payload = self._read_payload(second_event)
        self.event_1.process()
        self.event_2.process()
        assert self.event_1.pull_request_id == self.event_2.pull_request_id
        assert self.event_1.pull_request_id.state == 'open'

    @data(
        ('pull_request_1_merged.json', 'Add module account_show_full_features'),
        ('pull_request_2_closed.json', 'Add better logging'),
    )
    @unpack
    def test_title(self, filename, expected_title):
        self.event_1.payload = self._read_payload(filename)
        self.event_1.process()
        assert self.event_1.pull_request_id.title == expected_title
