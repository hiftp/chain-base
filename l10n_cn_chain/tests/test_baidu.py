from unittest import TestCase
from ..baidu import BaidubceProvider
from .. import CloudProvider


class TestBaidubceProvider(TestCase):
    def setUp(self):
        self._app = CloudProvider(BaidubceProvider)
        self._app.open()

    def test_address_recognition(self):
        ret = self._app.recognition("address", "上海市松江区中心路1238号11号楼707")
        self.fail()
