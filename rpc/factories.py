# Copyright The IETF Trust 2023, All Rights Reserved

import datetime

import factory
from django.db.models import Max

from .models import (
    ActionHolder,
    Assignment,
    Capability,
    Cluster,
    DispositionName,
    FinalApproval,
    Label,
    RfcAuthor,
    RfcToBe,
    RpcAuthorComment,
    RpcPerson,
    RpcRole,
    SourceFormatName,
    StdLevelName,
    StreamName,
    TlpBoilerplateChoiceName,
    UnusableRfcNumber,
)


class RpcPersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RpcPerson
        django_get_or_create = ("datatracker_person",)

    datatracker_person = factory.SubFactory(
        "datatracker.factories.DatatrackerPersonFactory"
    )

    @factory.post_generation
    def can_hold_role(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for item in extracted:
            if isinstance(item, str):
                self.can_hold_role.add(RpcRoleFactory(slug=item, **kwargs))
            elif isinstance(item, RpcRole):
                self.can_hold_role.add(item)
            else:
                raise Exception(f"Cannot add {item} to can_hold_role")

    @factory.post_generation
    def capable_of(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for item in extracted:
            if isinstance(item, str):
                self.capable_of.add(CapabilityFactory(slug=item, **kwargs))
            elif isinstance(item, Capability):
                self.capable_of.add(item)
            else:
                raise Exception(f"Cannot add {item} to can_hold_role")


class RpcRoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RpcRole
        django_get_or_create = ("slug",)

    slug = factory.Faker("word")
    name = factory.Faker("sentence")
    desc = factory.Faker("sentence")


class CapabilityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Capability
        django_get_or_create = ("slug",)

    slug = factory.Faker("word")
    name = factory.Faker("sentence")
    desc = factory.Faker("sentence")


class DispositionNameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DispositionName
        django_get_or_create = ("slug",)

    slug = factory.Faker("word")
    name = factory.Faker("sentence")
    desc = factory.Faker("sentence")


class RfcToBeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RfcToBe

    disposition = factory.SubFactory(DispositionNameFactory, slug="in_progress")
    draft = factory.SubFactory(
        "datatracker.factories.DocumentFactory",
        name=factory.Faker("sentence"),
        pages=factory.Faker("random_int", min=1, max=100),
    )
    submitted_format = factory.SubFactory(
        "rpc.factories.SourceFormatNameFactory", slug="xml-v3"
    )
    submitted_std_level = factory.SubFactory(
        "rpc.factories.StdLevelNameFactory", slug="ps"
    )
    submitted_boilerplate = factory.SubFactory(
        "rpc.factories.TlpBoilerplateChoiceNameFactory", slug="trust200902"
    )
    submitted_stream = factory.SubFactory(
        "rpc.factories.StreamNameFactory", slug="ietf"
    )
    intended_std_level = factory.LazyAttribute(lambda o: o.submitted_std_level)
    intended_boilerplate = factory.LazyAttribute(lambda o: o.submitted_boilerplate)
    intended_stream = factory.LazyAttribute(lambda o: o.submitted_stream)
    external_deadline = factory.Faker(
        "date_time_between",
        start_date="+1d",
        end_date="+15d",
        tzinfo=datetime.UTC,
    )


class AprilFirstRfcToBeFactory(RfcToBeFactory):
    is_april_first_rfc = True
    draft = None


class RfcToBeActionHolderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActionHolder

    datatracker_person = factory.SubFactory(
        "datatracker.factories.DatatrackerPersonFactory"
    )
    target_rfctobe = factory.SubFactory(RfcToBeFactory)
    comment = factory.Faker("sentence")


class RpcAuthorCommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RpcAuthorComment

    datatracker_person = factory.SubFactory(
        "datatracker.factories.DatatrackerPersonFactory"
    )
    comment = factory.Faker("sentence")
    by = factory.SubFactory("datatracker.factories.DatatrackerPersonFactory")


class ClusterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cluster
        django_get_or_create = ("number",)

    number = factory.LazyFunction(
        lambda: 1 + (Cluster.objects.aggregate(Max("number"))["number__max"] or 0)
    )


class UnusableRfcNumberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UnusableRfcNumber

    number = factory.LazyFunction(
        lambda: 1
        + (UnusableRfcNumber.objects.aggregate(Max("number"))["number__max"] or 0)
    )
    comment = factory.Faker("sentence")


class AssignmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Assignment

    rfc_to_be = factory.SubFactory(RfcToBeFactory)
    role = factory.SubFactory(RpcRoleFactory)
    person = factory.SubFactory(RpcPersonFactory)


class RfcAuthorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RfcAuthor

    datatracker_person = factory.SubFactory(
        "datatracker.factories.DatatrackerPersonFactory"
    )
    rfc_to_be = factory.SubFactory(RfcToBeFactory)
    order = factory.Sequence(lambda n: n + 1)


class FinalApprovalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FinalApproval

    rfc_to_be = factory.SubFactory(RfcToBeFactory)
    approver = factory.SubFactory("datatracker.factories.DatatrackerPersonFactory")


class SourceFormatNameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SourceFormatName
        django_get_or_create = ("slug",)


class StdLevelNameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StdLevelName
        django_get_or_create = ("slug",)


class TlpBoilerplateChoiceNameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TlpBoilerplateChoiceName
        django_get_or_create = ("slug",)


class StreamNameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StreamName
        django_get_or_create = ("slug",)


class LabelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Label
        django_get_or_create = ("slug",)

    color = "fuchsia"
