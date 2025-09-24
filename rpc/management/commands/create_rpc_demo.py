# Copyright The IETF Trust 2023, All Rights Reserved

import datetime

import rpcapi_client
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from datatracker.rpcapi import with_rpcapi

from ...factories import (
    AssignmentFactory,
    ClusterFactory,
    LabelFactory,
    RfcToBeActionHolderFactory,
    RfcToBeFactory,
    RpcPersonFactory,
)
from ...models import Assignment, ClusterMember, Label, RfcToBe, RpcPerson


class Command(BaseCommand):
    help = "Populate data for RPC Tools Refresh demo"

    def handle(self, *args, **options):
        self.people: dict[str, RpcPerson] = {}
        self.create_rpc_people()
        self.create_documents()
        self.create_real_people()

    @with_rpcapi
    def create_real_people(self, *, rpcapi: rpcapi_client.PurpleApi):
        """Create RpcPerson / DatatrackerPerson records for real people"""
        self.people["jennifer"] = RpcPersonFactory(
            datatracker_person__datatracker_id=rpcapi.get_subject_person_by_id(
                subject_id="14733"
            ).id,
            can_hold_role=["manager"],
        )
        self.people["robert"] = RpcPersonFactory(
            datatracker_person__datatracker_id=rpcapi.get_subject_person_by_id(
                subject_id="420"
            ).id,
            can_hold_role=["manager"],
        )
        self.people["jean"] = RpcPersonFactory(
            datatracker_person__datatracker_id=rpcapi.get_subject_person_by_id(
                subject_id="2706"
            ).id,
            can_hold_role=["manager"],
        )
        self.people["sandy"] = RpcPersonFactory(
            datatracker_person__datatracker_id=rpcapi.get_subject_person_by_id(
                subject_id="5709"
            ).id,
            can_hold_role=["manager"],
        )
        self.people["alice"] = RpcPersonFactory(
            datatracker_person__datatracker_id=rpcapi.get_subject_person_by_id(
                subject_id="2173"
            ).id,
            can_hold_role=["manager"],
        )

    @with_rpcapi
    def create_rpc_people(self, *, rpcapi: rpcapi_client.PurpleApi):
        # From "Manage Team Members" wireframe

        self.people["bjenkins"] = RpcPersonFactory(
            datatracker_person__datatracker_id=rpcapi.create_demo_person(
                rpcapi_client.DemoPersonCreateRequest(name="B. Jenkins"),
            ).person_pk,
            can_hold_role=[
                "formatting",
                "first_editor",
                "second_editor",
                "final_review_editor",
                "publisher",
                "manager",
            ],
            capable_of=[
                "codecomp-abnf",
                "codecomp-xml",
                "codecomp-yang",
                "clusters-expert",
                "ianaconsid-intermediate",
                "xmlfmt-intermediate",
            ],
        )
        self.people["atravis"] = RpcPersonFactory(
            datatracker_person__datatracker_id=rpcapi.create_demo_person(
                rpcapi_client.DemoPersonCreateRequest(name="A. Travis"),
            ).person_pk,
            can_hold_role=["formatting", "first_editor", "final_review_editor"],
            capable_of=["codecomp-abnf", "clusters-beginner", "ianaconsid-beginner"],
            manager=self.people["bjenkins"],
        )
        self.people["cbrown"] = RpcPersonFactory(
            datatracker_person__datatracker_id=rpcapi.create_demo_person(
                rpcapi_client.DemoPersonCreateRequest(name="Chuck Brown"),
            ).person_pk,
            can_hold_role=["formatting"],
            capable_of=["clusters-beginner"],
            manager=self.people["bjenkins"],
        )
        self.people["csimmons"] = RpcPersonFactory(
            datatracker_person__datatracker_id=rpcapi.create_demo_person(
                rpcapi_client.DemoPersonCreateRequest(name="C. Simmons"),
            ).person_pk,
            can_hold_role=[
                "formatting",
                "first_editor",
                "second_editor",
                "final_review_editor",
            ],
            capable_of=[
                "codecomp-abnf",
                "codecomp-mib",
                "clusters-intermediate",
                "ianaconsid-beginner",
                "xmlfmt-intermediate",
            ],
            manager=self.people["bjenkins"],
        )
        self.people["ffermat"] = RpcPersonFactory(
            datatracker_person__datatracker_id=rpcapi.create_demo_person(
                rpcapi_client.DemoPersonCreateRequest(name="F. Fermat"),
            ).person_pk,
            can_hold_role=[
                "formatting",
                "first_editor",
                "second_editor",
                "final_review_editor",
                "publisher",
            ],
            capable_of=[
                "codecomp-yang",
                "clusters-intermediate",
                "ianaconsid-beginner",
                "xmlfmt-expert",
            ],
            manager=self.people["bjenkins"],
        )
        self.people["kstrawberry"] = RpcPersonFactory(
            datatracker_person__datatracker_id=rpcapi.create_demo_person(
                rpcapi_client.DemoPersonCreateRequest(name="K. Strawberry"),
            ).person_pk,
            can_hold_role=["formatting", "first_editor"],
            capable_of=["ianaconsid-beginner", "xmlfmt-beginner"],
            manager=self.people["bjenkins"],
        )
        self.people["obleu"] = RpcPersonFactory(
            datatracker_person__datatracker_id=rpcapi.create_demo_person(
                rpcapi_client.DemoPersonCreateRequest(name="O. Bleu"),
            ).person_pk,
            can_hold_role=[
                "formatting",
                "first_editor",
                "second_editor",
                "final_review_editor",
            ],
            capable_of=[
                "codecomp-abnf",
                "codecomp-xml",
                "codecomp-yang",
                "clusters-expert",
                "ianaconsid-intermediate",
                "xmlfmt-intermediate",
            ],
            manager=self.people["bjenkins"],
        )
        self.people["pparker"] = RpcPersonFactory(
            datatracker_person__datatracker_id=rpcapi.create_demo_person(
                rpcapi_client.DemoPersonCreateRequest(name="Patricia Parker"),
            ).person_pk,
            can_hold_role=[
                "formatting",
                "first_editor",
                "second_editor",
                "final_review_editor",
            ],
            capable_of=[
                "codecomp-abnf",
                "codecomp-xml",
                "codecomp-yang",
                "clusters-expert",
                "ianaconsid-expert",
                "xmlfmt-expert",
            ],
            manager=self.people["bjenkins"],
        )
        self.people["sbexar"] = RpcPersonFactory(
            datatracker_person__datatracker_id=rpcapi.create_demo_person(
                rpcapi_client.DemoPersonCreateRequest(name="S. Bexar"),
            ).person_pk,
            can_hold_role=[
                "formatting",
                "first_editor",
                "second_editor",
                "final_review_editor",
                "publisher",
            ],
            capable_of=[
                "codecomp-abnf",
                "codecomp-mib",
                "codecomp-xml",
                "clusters-expert",
                "ianaconsid-expert",
                "xmlfmt-expert",
            ],
            manager=self.people["bjenkins"],
        )
        self.people["tlangfeld"] = RpcPersonFactory(
            datatracker_person__datatracker_id=rpcapi.create_demo_person(
                rpcapi_client.DemoPersonCreateRequest(name="T. Langfeld"),
            ).person_pk,
            can_hold_role=["formatting", "first_editor"],
            capable_of=["ianaconsid-beginner", "xmlfmt-beginner"],
            manager=self.people["bjenkins"],
        )
        self.people["ugarrison"] = RpcPersonFactory(
            datatracker_person__datatracker_id=rpcapi.create_demo_person(
                rpcapi_client.DemoPersonCreateRequest(name="U. Garrison"),
            ).person_pk,
            can_hold_role=["formatting"],
            capable_of=["xmlfmt-expert"],
            manager=self.people["bjenkins"],
        )

    @with_rpcapi
    def create_documents(self, *, rpcapi: rpcapi_client.PurpleApi):
        # submission, not yet an RfcToBe (not shown on "The Queue" wireframe)
        rpcapi.create_demo_draft(
            rpcapi_client.DemoDraftCreateRequest(
                name="draft-ietf-lizard-qol",
                rev="00",
                states=[("draft-iesg", "pub-req")],
            )
        )

        # submission, in cluster, pending assignment
        cluster783 = ClusterFactory(number=783)
        draft_foo_bar = self._demo_rfctobe_factory(
            rpcapi=rpcapi,
            name="draft-ietf-foo-bar",
            rev="03",
            states=[("draft-iesg", "rfcqueue")],
        )
        draft_foo_basbis = self._demo_rfctobe_factory(
            rpcapi=rpcapi,
            name="draft-ietf-foo-basbis",
            rev="19",
            states=[("draft-iesg", "rfcqueue")],
        )
        ClusterMember.objects.create(
            cluster=cluster783,
            doc=draft_foo_bar.draft,
            order=1,
        )
        ClusterMember.objects.create(
            cluster=cluster783,
            doc=draft_foo_basbis.draft,
            order=2,
        )

        # Exceptions:
        # <!> Stream hold - a stream manager has temporarily halted RPC work on the doc
        # and will let us know when we can start on it again
        # <!> Missing norm ref - the document is part of a cluster and one of its
        # normative references is not in the queue yet
        # <!> IANA action - RPC is waiting for IANA to update or create the registry
        # for this doc
        # Informational labels to help with assignments:
        # IANA Considerations - the document has an IANA Considerations section
        # ABNF - the document contains ABNF sourcecode
        # Needs Formatting - the document requires an XML expert to format complex
        # tables, nested lists, etc.
        LabelFactory(slug="Stream Hold", is_exception=True, color="yellow")
        LabelFactory(slug="Missing norm ref", is_exception=True, color="pink")
        LabelFactory(slug="IANA Hold", is_exception=True, color="rose")
        LabelFactory(slug="Tools Issue", color="neutral")
        LabelFactory(slug="ABNF", color="emerald")
        LabelFactory(slug="Needs Formatting", color="indigo")

        # Draft sent to RPC and in progress as an RfcToBe
        rfctobe = self._demo_rfctobe_factory(
            rpcapi=rpcapi,
            name="draft-ietf-tasty-cheese",
            rev="00",
            states=[("draft-iesg", "rfcqueue")],
        )
        rfctobe.labels.add(LabelFactory(slug="delicious"))
        rfctobe.labels.add(Label.objects.get(slug="Missing norm ref"))
        AssignmentFactory(
            rfc_to_be=RfcToBe.objects.get(draft__name="draft-ietf-tasty-cheese"),
            role__slug="first_editor",
            person=self.people["atravis"],
            state=Assignment.State.ASSIGNED,
        )
        AssignmentFactory(
            rfc_to_be=RfcToBe.objects.get(draft__name="draft-ietf-tasty-cheese"),
            role__slug="formatting",
            person=self.people["kstrawberry"],
            state=Assignment.State.IN_PROGRESS,
        )

        rfctobe = self._demo_rfctobe_factory(
            rpcapi=rpcapi,
            name="draft-ietf-where-is-my-hat",
            rev="04",
            states=[("draft-iesg", "rfcqueue")],
        )
        rfctobe.labels.add(
            LabelFactory(slug="is_a_trap", is_exception=True, color="red")
        )
        AssignmentFactory(
            rfc_to_be=RfcToBe.objects.get(draft__name="draft-ietf-where-is-my-hat"),
            role__slug="second_editor",
            person=self.people["sbexar"],
            state=Assignment.State.IN_PROGRESS,
        )

        self._demo_rfctobe_factory(
            rpcapi=rpcapi,
            name="draft-irtf-improving-lizard-qol",
            rev="07",
            stream="irtf",
            states=[("draft-iesg", "idexists")],
        )
        AssignmentFactory(
            rfc_to_be=RfcToBe.objects.get(
                draft__name="draft-irtf-improving-lizard-qol"
            ),
            role__slug="final_review_editor",
            person=self.people["sbexar"],
            state=Assignment.State.ASSIGNED,
        )
        RfcToBeActionHolderFactory(
            target_rfctobe=RfcToBe.objects.get(
                draft__name="draft-irtf-improving-lizard-qol"
            ),
            datatracker_person__datatracker_id=rpcapi.create_demo_person(
                rpcapi_client.DemoPersonCreateRequest(name="Artimus Ad"),
            ).person_pk,
            deadline=datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=14),
        )

        #
        # # Draft published as an RFC
        # rfc_number = next_rfc_number()[0]
        # RfcToBeFactory(
        #     disposition__slug="published",
        #     rfc_number=rfc_number,
        #     draft=WgRfcFactory(alias2__name=f"rfc{rfc_number}")
        # )

    @with_rpcapi
    def _demo_rfctobe_factory(
        self,
        *,
        rpcapi: rpcapi_client.PurpleApi,
        name,
        rev,
        states=None,
        stream="ietf",
        **kwargs,
    ):
        """Create a document on the back end and generate an RfcToBe linked to it

        **kwargs are passed through to the RfcToBeFactory
        """
        resp = rpcapi.create_demo_draft(
            rpcapi_client.DemoDraftCreateRequest(
                name=name, rev=rev, states=states, stream=stream
            )
        )
        dtdoc = rpcapi.get_draft_by_id(resp.doc_id)
        try:
            rfctobe = RfcToBeFactory(
                **kwargs,
                draft__datatracker_id=dtdoc.id,
                draft__name=dtdoc.name,
                draft__rev=dtdoc.rev,
                draft__title=dtdoc.title,
                draft__stream=dtdoc.stream,
                draft__pages=dtdoc.pages,
            )
            return rfctobe
        except IntegrityError:
            print(
                f">>> Warning: Failed to create RfcToBe for {dtdoc.name}, already "
                "exists?"
            )
