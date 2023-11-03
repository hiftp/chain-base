# -*- coding: utf-8 -*-
from unittest import TestCase
from ..wechat import WechatProvider
from .. import CloudProvider

from odoo import api, exceptions, fields, models, _


class TestWechatProvider(TestCase):
    def setUp(self):
        self._app = CloudProvider(WechatProvider)
        self._app.open()

    def test_auth(self):
        ret = self._app.auth(code="031pgl1w3lCAjX2pVH3w3baLYh2pgl10")
        print(ret)
        self.assertTrue(ret)
