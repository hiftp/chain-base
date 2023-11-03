# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import ValidationError
import os
from requests import Response as httpResponse
import time
import base64
import hashlib
import logging
import hmac
from typing import Optional

try:
    from .http import http_request
except ImportError:
    from odoo.addons.oneshare_utils.http import http_request

ENV_DINGTALK_CLIENT_ID = os.getenv("ENV_DINGTALK_CLIENT_ID", "")
ENV_DINGTALK_CLIENT_SECRET = os.getenv("ENV_DINGTALK_CLIENT_SECRET", "")

_logger = logging.getLogger(__name__)


def sign(secret, timestamp):
    """
    钉钉api签名函数
    :param secret: 钉钉app的secret
    :param timestamp: 目前时间戳
    :return: app的secret对时间戳进行sha256加密并base64的结果
    """
    msg = timestamp
    signature = hmac.new(
        secret.encode("utf-8"), msg.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()

    return base64.b64encode(signature)


class DingTalkProvider(object):
    def __init__(
        self, client_id=ENV_DINGTALK_CLIENT_ID, client_secret=ENV_DINGTALK_CLIENT_SECRET
    ):
        self._client_id = client_id
        self._client_secret = client_secret

    @staticmethod
    def open():
        return True

    def validate_by_code(self, validate_endpoint=None, code=None) -> httpResponse:
        if not validate_endpoint:
            validate_endpoint = "https://oapi.dingtalk.com/sns/getuserinfo_bycode"
        if not code:
            raise ValidationError("DingTalk Validate By Code, Code Is Empty!!!")
        # https://developers.dingtalk.com/document/app/queries-basic-user-information
        timestamp = str(int(time.time() * 1e3))
        params = {
            "accessKey": self._client_id,  # appId
            "timestamp": timestamp,
            "signature": sign(self._client_secret, timestamp),
        }
        resp: Optional[httpResponse] = self._do_validate_by_code(
            url=validate_endpoint, params=params, code=code
        )
        if resp:
            _logger.debug(f"DingTalk Validate By Code Resp: {resp.text}")
        return resp

    @http_request()
    def _do_validate_by_code(self, *args, **kwargs):
        data = {
            "tmp_auth_code": kwargs.get("code", ""),
        }
        return data
