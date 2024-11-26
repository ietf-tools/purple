# Copyright The IETF Trust 2024, All Rights Reserved
"""Development-mode Django settings for RPC project"""

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-gdr8b*13^h9uk#bw$cy#@=-fu_9=&@4^#e&#(b7u3rcbqs_#cl"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Datatracker
DATATRACKER_RPC_API_TOKEN = os.environ["PURPLE_RPC_API_TOKEN"]
DATATRACKER_RPC_API_BASE = "http://host.docker.internal:8000/api/rpc"
DATATRACKER_API_V1_BASE = "http://host.docker.internal:8000/api/v1"
DATATRACKER_BASE = "http://localhost:8000"


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
    }
}
