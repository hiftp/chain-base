# -*- encoding: utf-8 -*-
from aip.nlp import AipNlp
from distutils.util import strtobool
import os

ENV_BCE_APP_ID = os.getenv("ENV_BCE_APP_ID", "")
ENV_BCE_API_KEY = os.getenv("ENV_BCE_API_KEY", "")
ENV_BCE_SECRET_KEY = os.getenv("ENV_BCE_SECRET_KEY", "")


class BaidubceProvider(object):
    def __init__(
        self,
        app_id=ENV_BCE_APP_ID,
        api_key=ENV_BCE_API_KEY,
        secret_key=ENV_BCE_SECRET_KEY,
    ):
        self._app_id = app_id
        self._api_key = api_key
        self._secret_key = secret_key
        self._app = None

    def open(self):
        self._app = AipNlp(self._app_id, self._api_key, self._secret_key)

    def address_recognition(self, text):
        if self._app:
            return self._app.address(text)
        return None

    def recognition(self, type, *args, **kargs):
        name = f"{type}_recognition"
        method = getattr(self, name, None)
        if method:
            return method(*args, **kargs)
        return None
