# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import os
from odoo.tests import common


class GithubEventCase(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event_1 = cls.env['github.event'].create({})
        cls.event_2 = cls.env['github.event'].create({})

    def _read_payload(self, filename):
        test_folder = os.path.dirname(os.path.realpath(__file__))
        payload_file_path = os.path.join(test_folder, 'data', filename)
        with open(payload_file_path, 'r') as file:
            return file.read()
