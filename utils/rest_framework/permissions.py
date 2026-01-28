# Copyright The IETF Trust 2024-2026, All Rights Reserved
#
# Originated in ietf.api.permissions in datatracker
from rest_framework import permissions

from utils.apitoken import is_valid_token


class HasApiKey(permissions.BasePermission):
    """Permissions class that validates a token using is_valid_token

    The view class must indicate the relevant endpoint by setting `api_key_endpoint`.
    Must be used with an Authentication class that puts a token in request.auth.
    """

    def has_permission(self, request, view):
        endpoint = getattr(view, "api_key_endpoint", None)
        auth_token = getattr(request, "auth", None)
        if endpoint is not None and auth_token is not None:
            return is_valid_token(endpoint, auth_token)
        return False
