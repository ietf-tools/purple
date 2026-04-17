# Copyright The IETF Trust 2023, All Rights Reserved

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from datatracker.models import DatatrackerPerson
from rpc.models import RpcPerson, RpcRole


class User(AbstractUser):
    """RPC tool user class"""

    name = models.CharField(
        max_length=255,
        help_text="User's name",
    )

    datatracker_subject_id = models.CharField(
        max_length=255,  # per OpenID Core 1.0, 255 ASCII chars is the limit
        null=True,
        unique=True,
        help_text="Datatracker's subject ID for this User",
    )

    avatar = models.URLField(blank=True)

    def datatracker_person(self) -> DatatrackerPerson | None:
        try:
            dt_person, _ = DatatrackerPerson.objects.first_or_create_by_subject_id(
                self.datatracker_subject_id
            )
        except DatatrackerPerson.DoesNotExist:
            dt_person = None
        return dt_person

    def rpcperson(self) -> RpcPerson | None:
        datatracker_person = self.datatracker_person()
        if datatracker_person is None:
            return None
        try:
            rpcperson = datatracker_person.rpcperson
        except ObjectDoesNotExist:
            return None
        return rpcperson

    def set_is_manager(self, value: bool) -> None:
        """Add or remove the manager can_hold_role entry on this user's RpcPerson."""
        rpcperson = self.rpcperson()
        if rpcperson is None:
            return
        manager_role = RpcRole.objects.filter(slug="manager").first()
        if manager_role is None:
            return
        if value:
            rpcperson.can_hold_role.add(manager_role)
        else:
            rpcperson.can_hold_role.remove(manager_role)
