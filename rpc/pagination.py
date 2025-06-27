# Copyright The IETF Trust 2025, All Rights Reserved
from rest_framework.pagination import LimitOffsetPagination


class DefaultLimitOffsetPagination(LimitOffsetPagination):
    """Custom LimitOffset pagination class

    n.b., the "Default-" prefix is meant to suggest using this class by default -
    it's intended
    to be the standard pagination class for the RPC app.
    """

    # Setting a default ensures the pagination fields are always present in the
    # response. Without it, the OpenAPI schema gives a grossly wrong response schema
    default_limit = 100
