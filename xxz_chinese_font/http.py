# -*- encoding: utf-8 -*-

from http import HTTPStatus
from odoo.http import Response as odooResponse
from requests import Response as httpResponse
from odoo.tools import ustr
from odoo.exceptions import UserError
import logging
import pprint
import functools

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
import json
import requests
import copy
from tenacity import retry, wait_random_exponential, RetryError
from json import JSONEncoder
import datetime

_logger = logging.getLogger(__name__)

MAGIC_ERROR_CODE = 59999  # 永远不会定义

DEFAULT_METHOD = "post"

DEFAULT_HEADERS = {"Content-Type": "application/json"}

ONESHARE_HTTP_ERROR_CODE = {40001: "Tightening Tool Is Not Success Configuration"}


def _default_headers():
    return copy.deepcopy(DEFAULT_HEADERS)


def oneshare_http_request_stop(retry_state):
    if isinstance(retry_state.outcome, ValueError) or retry_state.attempt_number >= 5:
        return True
    else:
        return False


HTTP_METHOD_MODE = Literal["get", "post", "put", "delete", "options", "head"]


@retry(
    stop=oneshare_http_request_stop,
    wait=wait_random_exponential(multiplier=1, min=2, max=60),
    reraise=True,
)
def _send_request(
    full_url, method: HTTP_METHOD_MODE, headers, data, params=None, auth=None, timeout=6
):
    m = getattr(requests, method)
    if not m:
        raise ValueError("Can Not Found The Method: {}".format(method))
    if method in ["get"]:
        return m(
            url=full_url, params=params, headers=headers, timeout=timeout, auth=auth
        )
    if data and method in ["post", "put"]:
        payload = json.dumps(data)
    else:
        payload = None
    if payload:
        return m(
            url=full_url,
            data=payload,
            params=params,
            headers=headers,
            timeout=timeout,
            auth=auth,
        )
    else:
        return m(
            url=full_url, headers=headers, params=params, timeout=timeout, auth=auth
        )


def _do_http_request(
    url,
    method: HTTP_METHOD_MODE = DEFAULT_METHOD,
    data=None,
    headers=None,
    params=None,
    auth=None,
) -> httpResponse:
    if headers is None:
        headers = DEFAULT_HEADERS
    try:
        _logger.debug(
            "Do Request: {}, Data: {}".format(url, pprint.pformat(data, indent=4))
        )
        resp = _send_request(
            full_url=url,
            method=method,
            data=data,
            params=params,
            headers=headers,
            auth=auth,
        )
        if resp.status_code >= HTTPStatus.BAD_REQUEST:
            msg = f"Do Request: {url} Fail, Status Code: {resp.status_code}, resp: {resp.text}"
            _logger.error(msg)
            raise ValueError(msg)
        else:
            return resp
    except Exception as e:
        _logger.exception("HTTP Request URL:{} Except: {}".format(url, ustr(e)))
        raise e


def http_request(method: HTTP_METHOD_MODE = "post", url: str = "", auth=None):
    def decorator(f):
        @functools.wraps(f)
        def request_wrap(*args, **kw):
            rAuth = auth
            full_url = url
            if kw.get("auth") and not rAuth:
                rAuth = kw.get("auth")
            if kw.get("url") and not full_url:
                full_url = kw.get("url")
            data = f(*args, **kw) or {}
            if data and not isinstance(data, dict):
                raise ValueError(
                    "Function: {0}.{1}, HTTP Request Data Is Invalid".format(
                        f.__module__, f.__name__
                    )
                )
            headers = kw.get("headers") or _default_headers()
            if not method or not full_url:
                raise ValueError("Http Request, Params method & url Is Required")
            return _do_http_request(
                full_url,
                method=method,
                data=data,
                headers=headers,
                auth=rAuth,
                params=kw.get("params", None),
            )

        return request_wrap

    return decorator


# subclass JSONEncoder
class DateTimeEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


def oneshare_json_success_resp(
    status_code=HTTPStatus.OK, msg=None, extra=None, **kwargs
):
    headers = [("Content-Type", "application/json")]
    if status_code == HTTPStatus.NO_CONTENT:
        resp = odooResponse(status=status_code, headers=headers)
        return resp
    if status_code > HTTPStatus.BAD_REQUEST:
        _logger.error(
            "Success Response The Status Code Must Be Less Than 400, But Now Is {0}".format(
                status_code
            )
        )
        return odooResponse(HTTPStatus.OK, headers=headers)
    data = {"status_code": status_code, "msg": msg or "", **kwargs}
    if extra:
        data.update({"extra": extra})
    body = json.dumps(data, cls=DateTimeEncoder)
    headers.append(("Content-Length", len(body)))
    resp = odooResponse(body, status=status_code, headers=headers)
    return resp


def oneshare_json_fail_response(
    error_code=MAGIC_ERROR_CODE, status_code=HTTPStatus.BAD_REQUEST, **kwargs
):
    msg = ONESHARE_HTTP_ERROR_CODE.get(error_code)
    if not msg:
        _logger.error("Error Code: {0} Is Not Defined".format(error_code))
        msg = (kwargs.pop("msg", "") or kwargs.pop("message", ""),)
    data = {"status_code": status_code, "msg": msg, **kwargs}
    body = json.dumps(data, cls=DateTimeEncoder)
    headers = [("Content-Type", "application/json"), ("Content-Length", len(body))]
    return odooResponse(body, status=status_code, headers=headers)
