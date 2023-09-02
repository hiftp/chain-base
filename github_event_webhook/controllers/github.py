# © 2023 - Today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json
import hmac
import hashlib
from odoo import http
from odoo.http import request, Response
from werkzeug.urls import url_encode

import logging
_logger = logging.getLogger(__name__)

GITHUB_EVENT_SECRET_PARAM = 'github_pull_request.github_secret'
GITHUB_SIGNATURE_HEADER = 'X-Hub-Signature'


def make_github_signature(request_body: str, secret: str) -> str:
    """Make a Github signature from the given request body and secret.

    :param request_body: the request body
    :param secret: the secret (token)
    """
    digest = hmac.new(secret.encode(), request_body.encode(),
                      hashlib.sha1).hexdigest()
    return 'sha1={}'.format(digest)


def _get_github_signature_from_headers() -> str:
    return request.httprequest.headers.get(GITHUB_SIGNATURE_HEADER, "")


def _check_github_event_signature(signature: str) -> bool:
    request_body = url_encode(request.httprequest.form)
    secret = request.env['ir.config_parameter'].with_user(
        request.uid).get_param(GITHUB_EVENT_SECRET_PARAM)
    return make_github_signature(request_body, secret) == signature


class GithubEvent(http.Controller):

    @http.route('/web/github/event', type='http', auth='none', sitemap=False, csrf=False)
    def new_github_event(self, **data):
        signature = _get_github_signature_from_headers()

        if not signature:
            message = "The github signature is required to submit a new event."
            _logger.info(message)
            return Response(message, status=401)

        if not _check_github_event_signature(signature):
            message = "The given github signature is not valid."
            _logger.info(message)
            return Response(message, status=401)

        json_payload = self._get_json_payload(data)
        event = self._create_event(json_payload)
        event.with_delay().process_job()

        return Response(status=201)

    @staticmethod
    def _get_json_payload(data):
        return data['payload']

    @staticmethod
    def _create_event(json_payload):
        return request.env['github.event'].sudo().create({
            'payload': json_payload,
        })
