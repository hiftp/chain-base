# -*- encoding: utf-8 -*-

import os
import base64
from distutils.util import strtobool

import psutil

ENV_ONESHARE_EXPERIMENTAL_ENABLE = strtobool(
    os.getenv("ENV_ONESHARE_EXPERIMENTAL_ENABLE", "false")
)

ONESHARE_DEFAULT_LIMIT = int(os.getenv("ENV_ONESHARE_SQL_REC_LIMT", "15"))
ENV_ONESHARE_CRYPT_NONCE = os.getenv("ENV_ONESHARE_CRYPT_NONCE", "MTIzNDU2Nzg5MDEy")
ENV_ONESHARE_CRYPT_ASSOCIATED_DATA = os.getenv(
    "ENV_ONESHARE_CRYPT_ASSOCIATED_DATA",
    "QXV0aGVudGljYXRlZCBCeSBPbmVzaGFyZSBDby4gTHRkLg==",
)

ONESHARE_CRYPT_NONCE = base64.b64decode(ENV_ONESHARE_CRYPT_NONCE.encode("utf-8"))
ONESHARE_CRYPT_ASSOCIATED_DATA = base64.b64decode(
    ENV_ONESHARE_CRYPT_ASSOCIATED_DATA.encode("utf-8")
)

ENV_OSS_BUCKET = os.getenv("ENV_OSS_BUCKET", "oneshare")
ENV_OSS_ENDPOINT = os.getenv("ENV_OSS_ENDPOINT", "host.docker.internal:9000")
ENV_OSS_ACCESS_KEY = os.getenv("ENV_OSS_ACCESS_KEY", "minio")
ENV_OSS_SECRET_KEY = os.getenv("ENV_OSS_SECRET_KEY", "minio123")
ENV_OSS_SECURITY_TRANSPORT = strtobool(os.getenv("ENV_OSS_SECURITY_TRANSPORT", "false"))
ENV_OSS_EXPIRATION_DAYS = int(os.getenv("ENV_OSS_EXPIRATION_DAYS", "365"))

# SPC相关
ONESHARE_DEFAULT_SPC_MIN_LIMIT = int(os.getenv("ONESHARE_DEFAULT_SPC_MIN_LIMIT", "50"))
ONESHARE_DEFAULT_SPC_MAX_LIMIT = int(
    os.getenv("ONESHARE_DEFAULT_SPC_MAX_LIMIT", "1000")
)

DEFAULT_TIMEOUT = int(os.getenv("ONESHARE_DEFAULT_HTTP_TIMEOUT", "2"))  # 默认超时2s

ENV_MAX_WORKERS = int(os.getenv("ENV_MAX_WORKERS", str(psutil.cpu_count())))

ENV_HTTP_MAX_SIZE = int(os.getenv("ENV_HTTP_MAX_SIZE", "10"))  # 10MB
