# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.tests import common
from ddt import ddt, data, unpack

test_data = (
    ("https://github.com/Numigi/odoo_git_addons/pull/108693", "organization", "Numigi",),
    ("https://github.com/OCA/odoo_git_addons/pull/108693", "organization", "OCA",),
    ("https://www.github.com/Numigi/odoo_git_addons/pull/108693",
     "host", "www.github.com", ),
    ("https://github.com/Numigi/odoo_git_addons/pull/108693", "host", "github.com",),
    ("https://github.com/Numigi/odoo-git-addons/pull/108693",
     "repository", "odoo-git-addons",),
    ("https://github.com/Numigi/odoo_git_addons/pull/108693",
     "repository", "odoo_git_addons",),
    ("https://github.com/Numigi/odoo_git_addons/pull/1", "pull_request_number", 1,),
    ("https://github.com/Numigi/odoo_git_addons/pull/108693",
     "pull_request_number", 108693,),
)


@ddt
class TestPullRequest(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.github_pull_request_pool = cls.env["github.pull_request"]

    @data(*test_data)
    @unpack
    def test_whenPrIsCreatedFromURL_thenFieldsAreFilled(self, url, field, expected):
        pr = self.github_pull_request_pool.create({'source': url})
        assert pr[field] == expected

    @data(*test_data)
    @unpack
    def test_whenPrIsUpdatedFromURL_thenFieldsAreUpdated(self, url, field, expected):
        pr = self.github_pull_request_pool.create(
            {'source': "https://github.com/Numigi/odoo-public/pull/666"}
            # fake url, does not matter
        )
        pr.source = url
        assert pr[field] == expected
