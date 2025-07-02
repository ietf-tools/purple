# Copyright The IETF Trust 2023, All Rights Reserved

from functools import wraps
from urllib.parse import urlparse

import rpcapi_client
from django.conf import settings


class ApiClient(rpcapi_client.ApiClient):
    """ApiClient that obtains credentials and sets API base automatically"""

    def __init__(self):
        super().__init__(
            rpcapi_client.Configuration(
                host=settings.DATATRACKER_RPC_API_BASE,
                api_key={"apiKeyAuth": settings.DATATRACKER_RPC_API_TOKEN},
            )
        )

        # Include CF service tokens in the header if configured to do so
        if getattr(settings, "CF_SERVICE_TOKEN_HOSTS", None) is not None:
            if (
                urlparse(self.configuration.host).hostname
                in settings.CF_SERVICE_TOKEN_HOSTS
            ):
                self.default_headers["CF-Access-Client-Id"] = (
                    settings.CF_SERVICE_TOKEN_ID
                )
                self.default_headers["CF-Access-Client-Secret"] = (
                    settings.CF_SERVICE_TOKEN_SECRET
                )


def with_rpcapi(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "rpcapi" in kwargs:
            # Let an api instance be passed through
            return f(*args, **kwargs)

        # Create our own api instance and pass it to the wrapped function
        with ApiClient() as client:
            kwargs["rpcapi"] = rpcapi_client.PurpleApi(client)
            return f(*args, **kwargs)

    return wrapper
