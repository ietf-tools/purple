# Copyright The IETF Trust 2023, All Rights Reserved

import factory

from .models import (
    DatatrackerPerson,
    Document,
)


class DatatrackerPersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DatatrackerPerson
        django_get_or_create = ["datatracker_id"]

    datatracker_id = factory.Faker("pystr_format", string_format="######")


class DocumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Document
        django_get_or_create = ["datatracker_id"]

    datatracker_id = factory.Faker("pyint", min_value=1, max_value=10_000_000)
