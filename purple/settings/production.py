# Copyright The IETF Trust 2024, All Rights Reserved
"""Production-mode Django settings for RPC project"""

import json
import os
from hashlib import sha384

from .base import *


def _multiline_to_list(s):
    """Helper to split at newlines and convert to list"""
    return [item.strip() for item in s.split("\n") if item.strip()]


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["PURPLE_DJANGO_SECRET_KEY"]
assert not SECRET_KEY.startswith(
    "django-insecure"
)  # be sure we didn't get the dev secret

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# PURPLE_ALLOWED_HOSTS is a newline-separated list of allowed hosts
ALLOWED_HOSTS = _multiline_to_list(os.environ["PURPLE_ALLOWED_HOSTS"])

# Datatracker config
#
# For real production use, should not need to configure any of the env vars
# except PURPLE_RPC_API_TOKEN.
DATATRACKER_RPC_API_TOKEN = os.environ["PURPLE_RPC_API_TOKEN"]
DATATRACKER_BASE = os.environ.get(
    "PURPLE_DATATRACKER_BASE", "https://datatracker.ietf.org"
)
DATATRACKER_RPC_API_BASE = os.environ.get(
    "PURPLE_DATATRACKER_RPC_API_BASE", f"{DATATRACKER_BASE}/api/rpc"
)
DATATRACKER_API_V1_BASE = os.environ.get(
    "PURPLE_DATATRACKER_API_V1_BASE", f"{DATATRACKER_BASE}/api/v1"
)


# OIDC configuration (see also base.py)
OIDC_RP_CLIENT_ID = os.environ["PURPLE_OIDC_RP_CLIENT_ID"]
OIDC_RP_CLIENT_SECRET = os.environ["PURPLE_OIDC_RP_CLIENT_SECRET"]
OIDC_OP_ISSUER_ID = os.environ.get(
    "PURPLE_OIDC_OP_ISSUER_ID", f"{DATATRACKER_BASE}/api/openid"
)
OIDC_OP_JWKS_ENDPOINT = os.environ.get(
    "PURPLE_OIDC_OP_JWKS_ENDPOINT", f"{OIDC_OP_ISSUER_ID}/jwks/"
)
OIDC_OP_AUTHORIZATION_ENDPOINT = os.environ.get(
    "PURPLE_OIDC_OP_AUTHORIZATION_ENDPOINT", f"{OIDC_OP_ISSUER_ID}/authorize/"
)
OIDC_OP_TOKEN_ENDPOINT = os.environ.get(
    "PURPLE_OIDC_OP_TOKEN_ENDPOINT", f"{OIDC_OP_ISSUER_ID}/token/"
)
OIDC_OP_USER_ENDPOINT = os.environ.get(
    "PURPLE_OIDC_OP_USER_ENDPOINT", f"{OIDC_OP_ISSUER_ID}/userinfo/"
)
OIDC_OP_END_SESSION_ENDPOINT = os.environ.get(
    "PURPLE_OIDC_OP_END_SESSION_ENDPOINT", f"{OIDC_OP_ISSUER_ID}/end-session/"
)


# Config for Cloudflare service token auth
_CF_SERVICE_TOKEN_HOSTS = os.environ.get("PURPLE_SERVICE_TOKEN_HOSTS", None)
if _CF_SERVICE_TOKEN_HOSTS is not None:
    # include token id/secret headers for these hosts
    CF_SERVICE_TOKEN_HOSTS = _multiline_to_list(_CF_SERVICE_TOKEN_HOSTS)
    CF_SERVICE_TOKEN_ID = os.environ.get("PURPLE_SERVICE_TOKEN_ID", None)
    CF_SERVICE_TOKEN_SECRET = os.environ.get("PURPLE_SERVICE_TOKEN_SECRET", None)


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("PURPLE_DB_NAME"),
        "USER": os.environ.get("PURPLE_DB_USER"),
        "PASSWORD": os.environ.get("PURPLE_DB_PASS"),
        "HOST": os.environ.get("PURPLE_DB_HOST"),
        "PORT": int(os.environ.get("PURPLE_DB_PORT")),
        "OPTIONS": json.loads(os.environ.get("PURPLE_DB_OPTS_JSON", "{}")),
    }
}

# Configure persistent connections. A setting of 0 is Django's default.
_conn_max_age = os.environ.get("PURPLE_DB_CONN_MAX_AGE", "0")
# A string "none" means unlimited age.
DATABASES["default"]["CONN_MAX_AGE"] = (
    None if _conn_max_age.lower() == "none" else int(_conn_max_age)
)
# Enable connection health checks if PURPLE_DB_CONN_HEALTH_CHECK is the string "true"
_conn_health_checks = bool(
    os.environ.get("PURPLE_DB_CONN_HEALTH_CHECKS", "false").lower() == "true"
)
DATABASES["default"]["CONN_HEALTH_CHECKS"] = _conn_health_checks


# Caches
#
# Get memcached service host/port from k8s environment vars
_memcached_host = os.environ.get("MEMCACHED_SERVICE_HOST")
if _memcached_host is not None:
    _memcached_port = os.environ.get("MEMCACHED_SERVICE_PORT", "11211")
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
            "LOCATION": f"{_memcached_host}:{_memcached_port}",
            "KEY_PREFIX": "ietf:purple",
            "KEY_FUNCTION": lambda key, key_prefix, version: (
                f"{key_prefix}:{version}:{sha384(str(key).encode('utf8')).hexdigest()}"
            ),
            "TIMEOUT": 600,  # 10 minute default timeout
        }
    }
