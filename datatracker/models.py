# Copyright The IETF Trust 2023, All Rights Reserved
# -*- coding: utf-8 -*-

import rpcapi_client
from django.core.cache import cache

from datatracker.rpcapi import with_rpcapi

from django.db import models


class DatatrackerPersonQuerySet(models.QuerySet):
    @with_rpcapi
    def by_subject_id(self, subject_id, *, rpcapi: rpcapi_client.DefaultApi):
        try:
            dtpers = rpcapi.get_subject_person_by_id(subject_id=subject_id)
        except rpcapi_client.exceptions.NotFoundException:
            return super().none()
        return super().filter(datatracker_id=dtpers.id)


class DatatrackerPerson(models.Model):
    """Person known to the datatracker"""

    objects = DatatrackerPersonQuerySet.as_manager()

    # datatracker uses AutoField for this, which is only an IntegerField, but might as well go big
    datatracker_id = models.BigIntegerField(
        unique=True, help_text="ID of the Person in the datatracker"
    )

    def __str__(self):
        return f"Datatracker Person {self.datatracker_id}"

    @with_rpcapi
    def plain_name(self, *, rpcapi: rpcapi_client.DefaultApi):
        cache_key = f"datatracker_person-{self.datatracker_id}-plain_name"
        print(f"cache_key = {cache_key}")
        no_value = object()
        cached_value = cache.get(cache_key, no_value)
        if cached_value is no_value:
            print("cache miss")
            try:
                person = rpcapi.get_person_by_id(int(self.datatracker_id))
            except rpcapi_client.exceptions.NotFoundException:
                cached_value = None
            else:
                cached_value = person.plain_name
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
