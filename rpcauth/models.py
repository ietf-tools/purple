# Copyright The IETF Trust 2023, All Rights Reserved
# -*- coding: utf-8 -*-

from django.contrib.auth.models import AbstractUser
from django.db import models

from datatracker.models import DatatrackerPerson


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

    def datatracker_person(self):
        try:
            dt_person, _ = DatatrackerPerson.objects.get_or_create_by_subject_id(
                self.datatracker_subject_id
            )
        except DatatrackerPerson.DoesNotExist:
            dt_person = None
        return dt_person
