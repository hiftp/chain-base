# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from collections import OrderedDict
from odoo.addons.test_http_request.common import mock_odoo_request
from odoo.tests import common
from uuid import uuid4
from werkzeug.urls import url_encode
import json
from ..controllers.github import (
    GithubEvent,
    GITHUB_EVENT_SECRET_PARAM,
    GITHUB_SIGNATURE_HEADER,
    make_github_signature,
)


class TestPullRequest(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['github.event'].search([]).unlink()
        cls.token = str(uuid4())
        cls.env['ir.config_parameter'].set_param(
            GITHUB_EVENT_SECRET_PARAM, cls.token)

    def setUp(self):
        super().setUp()
        self.controller = GithubEvent()
        self.payload = OrderedDict([
            ('number', 1),
            ('action', 'created'),
        ])
        self.data = {'payload': json.dumps(self.payload)}
        encoded_data = url_encode(self.data)
        signature = make_github_signature(encoded_data, self.token)
        self.headers = {GITHUB_SIGNATURE_HEADER: signature}

    def _get_created_event(self):
        return self.env['github.event'].search([])

    def test_after_called__event_created(self):
        with mock_odoo_request(self.env, headers=self.headers, data=self.data):
            response = self.controller.new_github_event(**self.data)

        assert response.status_code == 201
        assert len(self._get_created_event()) == 1

    def test_event_created_with_payload(self):
        with mock_odoo_request(self.env, headers=self.headers, data=self.data):
            self.controller.new_github_event(**self.data)

        event = self._get_created_event()
        assert event.payload
        assert json.loads(event.payload) == self.payload

    def test_if_token_not_passed__return_error_401(self):
        del self.headers[GITHUB_SIGNATURE_HEADER]

        with mock_odoo_request(self.env, headers=self.headers, data=self.data):
            response = self.controller.new_github_event(**self.data)

        assert response.status_code == 401
        assert not self._get_created_event()

    def test_if_wrong_token_passed__return_error_401(self):
        self.headers[GITHUB_SIGNATURE_HEADER] = 'sha1={}'.format(str(uuid4()))

        with mock_odoo_request(self.env, headers=self.headers, data=self.data):
            response = self.controller.new_github_event(**self.data)

        assert response.status_code == 401
        assert not self._get_created_event()

    def test_after_called__queue_job_created(self):
        with mock_odoo_request(self.env, headers=self.headers, data=self.data):
            self.controller.new_github_event(**self.data)

        event = self._get_created_event()
        job = self.env['queue.job'].search([
            ('model_name', '=', 'github.event'),
            ('method_name', '=', 'process_job'),
        ]).filtered(lambda j: j.record_ids == [event.id])
        assert len(job) == 1
