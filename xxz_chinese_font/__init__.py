# -*- coding: utf-8 -*-
from . import models
from . import baidu
from . import http
from . import constants
from . import datetime
from . import wechat
from . import github
from . import dingtalk


class CloudProvider(object):
    def __init__(self, subclass=None, *args, **kwargs):
        self._subclass = subclass
        self._app = {}
        if subclass:
            self._app = self._subclass(*args, **kwargs)

    def address_recognition(self, text):
        raise NotImplementedError()

    def open(self):
        method = getattr(self._app, "open", None)
        if not method:
            return False
        return method()

    def recognition(self, type, *args, **kwargs):
        return self._app.recognition(type, *args, **kwargs)

    def auth(self, *args, **kwargs):
        return self._app.auth(*args, **kwargs)

    def invoke_api(self, evt: str = "", *args, **kwargs):
        return self._app.invoke_api(evt, *args, **kwargs)

    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError:
            return getattr(self._app, item)


