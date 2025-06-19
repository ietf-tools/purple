# Copyright The IETF Trust 2023-2025, All Rights Reserved
# -*- coding: utf-8 -*-
from typing import cast

import rpcapi_client
from django.core.cache import cache
from simple_history.models import HistoricalRecords

from datatracker.rpcapi import with_rpcapi

from django.db import models


class DatatrackerPersonQuerySet(models.QuerySet):
    @with_rpcapi
    def first_or_create_by_subject_id(
        self, subject_id, *, rpcapi: rpcapi_client.DefaultApi
    ) -> tuple["DatatrackerPerson", bool]:
        """Get an instance by subject id, creating it if necessary

        Like get_or_create(), but returns the first matching instance rather than raising
        an exception if more than one match is found.
        """
        try:
            dtpers = rpcapi.get_subject_person_by_id(subject_id=subject_id)
        except rpcapi_client.exceptions.NotFoundException:
            raise DatatrackerPerson.DoesNotExist
        try:
            return cast(
                tuple[DatatrackerPerson, bool],
                super().get_or_create(datatracker_id=dtpers.id),
            )
        except DatatrackerPerson.MultipleObjectsReturned:
            return DatatrackerPerson.objects.filter(
                datatracker_id=dtpers.id
            ).first(), False


class DatatrackerPerson(models.Model):
    """Person known to the datatracker"""

    objects = DatatrackerPersonQuerySet.as_manager()

    # datatracker uses AutoField for this, which is only an IntegerField, but might as well go big
    datatracker_id = models.BigIntegerField(
        help_text="ID of the Person in the datatracker"
    )
    history = HistoricalRecords()

    def __str__(self):
        return f"Datatracker Person {self.pk} ({self.datatracker_id})"

    class Meta:
        ordering = ["id"]

    @property
    def plain_name(self) -> str:
        return self._fetch("plain_name") or "<Unknown>"

    @property
    def picture(self) -> str:
        return self._fetch("picture")

    @with_rpcapi
    def _fetch(self, field_name, *, rpcapi: rpcapi_client.DefaultApi):
        """Get field_name value for person (uses cache)"""
        cache_key = f"datatracker_person-{self.datatracker_id}-{field_name}"
        no_value = object()
        cached_value = cache.get(cache_key, no_value)
        if cached_value is no_value:
            try:
                person = rpcapi.get_person_by_id(int(self.datatracker_id))
            except rpcapi_client.exceptions.NotFoundException:
                cached_value = None
            else:
                cached_value = getattr(person, field_name)
            cache.set(cache_key, cached_value)
        return cached_value


class Document(models.Model):
    """Document known to the datatracker"""

    # datatracker uses AutoField for this, which is only an IntegerField, but might as well go big
    datatracker_id = models.BigIntegerField(unique=True)

    name = models.CharField(max_length=255, unique=True, help_text="Name of draft")
    rev = models.CharField(max_length=16, help_text="Revision of draft")
    title = models.CharField(max_length=255, help_text="Title of draft")
    stream = models.CharField(max_length=32, help_text="Stream of draft")
    pages = models.PositiveSmallIntegerField(help_text="Number of pages")
    intended_std_level = models.CharField(max_length=32, blank=True)

    # Labels applied to this instance. To track history, see
    # https://django-simple-history.readthedocs.io/en/latest/historical_model.html#tracking-many-to-many-relationships
    labels = models.ManyToManyField("rpc.Label", through="DocumentLabel")

    def __str__(self):
        return f"{self.name}-{self.rev}"


class DocumentLabel(models.Model):
    """Through model for linking Label to Document

    This exists so we can specify on_delete=models.PROTECT for the label FK.
    """

    document = models.ForeignKey("Document", on_delete=models.CASCADE)
    label = models.ForeignKey("rpc.Label", on_delete=models.PROTECT)
