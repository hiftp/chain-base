#  Copyright (c) by The Bean Family, 2023.
#
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#  These code are maintained by The Bean Family.

import logging
import sys

from odoo import http, tools
from odoo.service import security
from odoo.tools._vendor.sessions import SessionStore

_logger = logging.getLogger(__name__)

# Import C library Pickle which is used to convert 'data' to stream of bytes
if sys.version_info > (3,):
    import _pickle as cPickle

    unicode = str
else:
    import cPickle

SESSION_TIMEOUT = 60 * 60 * 24 * 7  # 1 weeks in seconds


def is_redis_session_store_activated():
    return tools.config.get('ODOO_SESSION_REDIS')


# Check the existing of Redis library: https://pypi.org/project/redis/
try:
    import redis
except ImportError:
    if is_redis_session_store_activated():
        raise ImportError(
            'Please install package redis: '
            'pip install redis')


# Define the RedisSession Store Class
class RedisSessionStore(SessionStore):

    def __init__(self, *args, **kwargs):
        _logger.debug("Redis module is initialing ...")
        super(RedisSessionStore, self).__init__(*args, **kwargs)
        self.expire = kwargs.get('expire', SESSION_TIMEOUT)
        self.key_prefix = kwargs.get('key_prefix', '')
        self.redis = redis.Redis(
            host=tools.config.get('ODOO_SESSION_REDIS_HOST', 'localhost'),
            port=int(tools.config.get('ODOO_SESSION_REDIS_PORT', 6379)),
            db=int(tools.config.get('ODOO_SESSION_REDIS_DBINDEX', 0)),
            password=tools.config.get('ODOO_SESSION_REDIS_PASSWORD', None))
        self._is_redis_server_running()

    def save(self, session):
        key = self._get_session_key(session.sid)
        data = cPickle.dumps(dict(session))
        _logger.debug(f"Session key is {key} and will be save in redis.")
        self.redis.setex(name=key, value=data, time=self.expire)

    def rotate(self, session, env):
        self.delete(session)
        session.sid = self.generate_key()
        if session.uid and env:
            session.session_token = security.compute_session_token(session, env)
        session.should_rotate = False
        self.save(session)

    def delete(self, session):
        key = self._get_session_key(session.sid)
        self.redis.delete(key)

    def _get_session_key(self, sid):
        key = self.key_prefix + sid
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        return key

    def get(self, sid):
        key = self._get_session_key(sid)
        data = self.redis.get(key)
        if data:
            self.redis.setex(name=key, value=data, time=self.expire)
            data = cPickle.loads(data)
        else:
            data = {}
        return self.session_class(data, sid, False)

    def _is_redis_server_running(self):

        try:
            self.redis.ping()
            _logger.debug("Redis is running ...")
        except redis.ConnectionError:
            raise redis.ConnectionError('Redis server is not responding')


if is_redis_session_store_activated():
    # Patch methods of http to use Redis instead of filesystem
    http.Application.session_store = RedisSessionStore(session_class=http.Session)
