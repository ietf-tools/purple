# Copyright The IETF Trust 2026, All Rights Reserved
from rest_framework import permissions


def is_manager(user) -> bool:
    """Whether user may do what managers do: a superuser, or an RpcPerson holding
    the manager role (set from the login claims, see rpcauth)."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    rpcperson = user.rpcperson()
    return (
        rpcperson is not None
        and rpcperson.can_hold_role.filter(slug="manager").exists()
    )


class IsManager(permissions.BasePermission):
    message = "Only managers can do this."

    def has_permission(self, request, view):
        return is_manager(request.user)
