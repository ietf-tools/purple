# Copyright The IETF Trust 2023-2025, All Rights Reserved
from urllib.parse import urlsplit, urlunsplit

import rpcapi_client
from django.conf import settings
from django.core.cache import cache
from django.db import models
from simple_history.models import HistoricalRecords

from .rpcapi import with_rpcapi


class DatatrackerPersonQuerySet(models.QuerySet):
    @with_rpcapi
    def first_or_create(
        self, defaults=None, *, rpcapi: rpcapi_client.PurpleApi, **kwargs
    ):
        try:
            return self.get_or_create(defaults, **kwargs)
        except DatatrackerPerson.MultipleObjectsReturned:
            return DatatrackerPerson.objects.filter(**kwargs).first(), False

    @with_rpcapi
    def first_or_create_by_subject_id(
        self, subject_id, *, rpcapi: rpcapi_client.PurpleApi
    ) -> tuple["DatatrackerPerson", bool]:
        """Get an instance by subject id, creating it if necessary

        Like get_or_create(), but returns the first matching instance rather than
        raising an exception if more than one match is found.
        """
        try:
            dtpers = rpcapi.get_subject_person_by_id(subject_id=subject_id)
        except rpcapi_client.exceptions.NotFoundException as err:
            raise DatatrackerPerson.DoesNotExist() from err
        return self.first_or_create(datatracker_id=dtpers.id)


class DatatrackerPerson(models.Model):
    """Person known to the datatracker"""

    objects = DatatrackerPersonQuerySet.as_manager()

    # datatracker uses AutoField for this, which is only an IntegerField,
    # but might as well go big
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
    def email(self) -> str:
        return self._fetch("email") or "<Unknown>"

    @property
    def picture(self) -> str:
        return self._fetch("picture")

    @property
    def url(self) -> str:
        url = self._fetch("url")
        if url:
            # Equivalent to urljoin but overwrites scheme and netloc with
            # those from the base, even if url is an absolute URL. This ensures
            # we always link to the same datatracker instance purple is using for
            # other purposes, even in dev and staging environments. (As of now
            # the url should be relative, so this is just precautionary.)
            baseparts = urlsplit(settings.DATATRACKER_BASE)
            urlparts = urlsplit(url)._replace(
                scheme=baseparts.scheme,
                netloc=baseparts.netloc,
            )
            url = urlunsplit(urlparts)
        return url

    @with_rpcapi
    def _fetch(self, field_name, *, rpcapi: rpcapi_client.PurpleApi):
        """Get field_name value for person (uses cache)"""
        cache_key = f"datatracker_person-{self.datatracker_id}"
        no_value = object()
        cached_value = cache.get(cache_key, no_value)
        if cached_value is no_value:
            try:
                person = rpcapi.get_person_by_id(int(self.datatracker_id))
            except rpcapi_client.exceptions.NotFoundException:
                cached_value = None
            else:
                cached_value = person.json()
            cache.set(cache_key, cached_value)
        if cached_value is None:
            return None
        return getattr(
            rpcapi_client.models.person.Person.from_json(cached_value), field_name, None
        )


class Document(models.Model):
    """Document known to the datatracker"""

    # datatracker uses AutoField for this, which is only an IntegerField,
    # but might as well go big
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
