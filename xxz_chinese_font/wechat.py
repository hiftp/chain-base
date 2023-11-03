# -*- encoding: utf-8 -*-

import os
from wechatpy.client import WeChatClient
from wechatpy.client.api import WeChatWxa
import logging
from odoo.exceptions import UserError, ValidationError
from odoo.tools import ustr

_logger = logging.getLogger(__name__)

ENV_WECHAT_APP_ID = os.getenv("ENV_WECHAT_APP_ID", "")
ENV_WECHAT_SECRET_KEY = os.getenv("ENV_WECHAT_SECRET_KEY", "")


class WechatProvider(object):
    def __init__(self, app_id=ENV_WECHAT_APP_ID, secret_key=ENV_WECHAT_SECRET_KEY):
        self._app_id = app_id
        self._secret_key = secret_key
        self._client = WeChatClient(
            appid=self._app_id, secret=self._secret_key, timeout=60
        )
        self._session = None

    # success_resp = {'session_key': 'rCkMgTL/daaJ5vQTpfjMBQ==', 'openid': 'oEyZC5JY04tEfsc7mqGObfA7hZCw'}
    def auth(self, code: str = ""):
        ret = {}
        try:
            if not self._client:
                raise ValidationError("微信认证,请先创建客户端")
            if not code:
                raise ValidationError("微信认证,认证代码未获取")
            c = WeChatWxa(self._client)
            ret = c.code_to_session(code)
        except Exception as e:
            _logger.error(ustr(e))
        return ret
