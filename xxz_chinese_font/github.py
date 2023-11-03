# -*- encoding: utf-8 -*-

from requests import Response
from distutils.util import strtobool
from http import HTTPStatus

try:
    from .http import http_request
except ImportError:
    from odoo.addons.oneshare_utils.http import http_request
import os

ENV_GITHUB_ACCESS_TOKEN = os.getenv("ENV_GITHUB_ACCESS_TOKEN", "")
ENV_GITHUB_OWNER = os.getenv("ENV_GITHUB_OWNER", "")


class GithubProvider(object):
    def __init__(self, token=ENV_GITHUB_ACCESS_TOKEN):
        self._access_token = token
        self._repo_event_url_tmpl = f"https://api.github.com/repos/%s/%s/dispatches"
        self._repo_get_tags_url_tmpl = f"https://api.github.com/repos/%s/%s/tags"
        self._get_repos = f"https://api.github.com/user/repos"

    @staticmethod
    def open():
        return True

    def invoke_api(self, evt: str = "", *args, **kwargs):
        if evt == "repo_dispatch":
            repo = kwargs.get("repo", "")
            owner = kwargs.get("owner", "")
            client_payload = kwargs.get("client_payload", "")
            return self.trigger_repo_dispatch_evt(owner, repo, client_payload)
        if evt == "list_repos":
            return self.get_repos()
        if evt == "list_tags":
            repo = kwargs.get("repo", "")
            owner = kwargs.get("owner", "")
            return self.get_repo_tags(owner, repo)

    def get_repo_tags(self, owner, repo):
        if not repo or not owner:
            return
        url = self._repo_get_tags_url_tmpl % (
            owner,
            repo,
        )
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self._access_token}",
        }
        resp = self._do_get_repo_tags(url=url, headers=headers)
        if not isinstance(resp, Response):
            return None
        if resp.status_code != HTTPStatus.OK:
            return None
        data = resp.json()
        tags = []
        for tag in data:
            tags.append(tag.get("name"))
        return tags

    def get_repos(self):
        url = self._get_repos
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self._access_token}",
        }
        params = {"sort": "updated"}
        resp = self._do_get_all_repos(url=url, headers=headers, params=params)
        if not isinstance(resp, Response):
            return None
        if resp.status_code != HTTPStatus.OK:
            return None
        data = resp.json()
        repos = []
        for repo in data:
            repos.append(repo.get("full_name"))
        return repos

    @http_request(method="get")
    def _do_get_repo_tags(self, *args, **kwargs):
        return

    @http_request(method="get")
    def _do_get_all_repos(self, *args, **kwargs):
        data = {}
        return data

    def trigger_repo_dispatch_evt(self, owner="", repo="", client_payload: dict = None):
        if client_payload is None:
            client_payload = {}
        if not repo or not owner:
            return
        url = self._repo_event_url_tmpl % (
            owner,
            repo,
        )
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self._access_token}",
        }
        resp = self._do_trigger_repo_dispatch_evt(
            url=url, headers=headers, client_payload=client_payload
        )
        return resp

    @http_request()
    def _do_trigger_repo_dispatch_evt(self, *args, **kwargs):
        data = {
            "event_type": kwargs.get("event_type", "repo_dispatch"),
            "client_payload": kwargs.get("client_payload", {}),
        }
        return data
