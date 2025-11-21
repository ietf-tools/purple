# Copyright The IETF Trust 2024, All Rights Reserved
"""Development-mode Django settings for RPC project"""

import os

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-gdr8b*13^h9uk#bw$cy#@=-fu_9=&@4^#e&#(b7u3rcbqs_#cl"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Datatracker
DATATRACKER_RPC_API_TOKEN = os.environ["PURPLE_RPC_API_TOKEN"]
DATATRACKER_RPC_API_BASE = "http://host.docker.internal:8000"
DATATRACKER_API_V1_BASE = "http://host.docker.internal:8000/api/v1"
DATATRACKER_BASE = os.environ.get(
    "NUXT_PUBLIC_DATATRACKER_BASE",  # matches name used by Nuxt runtimeConfig
    "http://localhost:8000",
)


# OIDC configuration (see also base.py)
OIDC_RP_CLIENT_ID = os.environ["PURPLE_OIDC_RP_CLIENT_ID"]
OIDC_RP_CLIENT_SECRET = os.environ["PURPLE_OIDC_RP_CLIENT_SECRET"]
OIDC_OP_ISSUER_ID = "http://localhost:8000/api/openid"
OIDC_OP_JWKS_ENDPOINT = "http://host.docker.internal:8000/api/openid/jwks/"
OIDC_OP_AUTHORIZATION_ENDPOINT = (
    "http://localhost:8000/api/openid/authorize/"  # URL for user agent
)
OIDC_OP_TOKEN_ENDPOINT = "http://host.docker.internal:8000/api/openid/token/"
OIDC_OP_USER_ENDPOINT = "http://host.docker.internal:8000/api/openid/userinfo/"
OIDC_OP_END_SESSION_ENDPOINT = "http://localhost:8000/api/openid/end-session/"

# Misc
SESSION_COOKIE_NAME = (
    "rpcsessionid"  # need to set this if oidc provider is on same domain as client
)


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": "db",
        "PORT": 5432,
        "TEST": {
            "NAME": os.environ.get("POSTGRES_TEST_DB"),
        }
    }
}

# email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("PURPLE_EMAIL_HOST", "mailpit")
EMAIL_PORT = int(os.getenv("PURPLE_EMAIL_PORT", 1025))

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] += [
    "rest_framework.renderers.BrowsableAPIRenderer",
]

INSTALLED_APPS += [
    "debug_toolbar",
    "django_filters",
]

# Add debug toolbar middleware
MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# Add debug toolbar configuration
# set IPs where debug toolbar should be shown, might need to add local IPs for docker
# or comment out to disable toolbar
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# Local settings override
try:
    from .development_local import *
except ImportError:
    pass
