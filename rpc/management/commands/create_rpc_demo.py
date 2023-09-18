# Copyright The IETF Trust 2023, All Rights Reserved
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from ...factories import RpcPersonFactory


class Command(BaseCommand):
    help = "Populate data for RPC Tools Refresh demo"

    def handle(self, *args, **options):
        self.create_rpc_people()
        self.create_documents()

    def create_rpc_people(self):
        # From "Manage Team Members" wireframe
        bjenkins = RpcPersonFactory(
            datatracker_person__plain_name="B. Jenkins",
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
        RpcPersonFactory(
            datatracker_person__plain_name="A. Travis",
            can_hold_role=["formatting", "first_editor", "final_review_editor"],
            capable_of=["codecomp-abnf", "clusters-beginner", "ianaconsid-beginner"],
            manager=bjenkins,
        )
        RpcPersonFactory(
            datatracker_person__plain_name="Chuck Brown",
            can_hold_role=["formatting"],
            capable_of=["clusters-beginner"],
            manager=bjenkins,
        )
        RpcPersonFactory(
            datatracker_person__plain_name="C. Simmons",
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
            manager=bjenkins,
        )
        RpcPersonFactory(
            datatracker_person__plain_name="F. Fermat",
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
            manager=bjenkins,
        )
        RpcPersonFactory(
            datatracker_person__plain_name="K. Strawberry",
            can_hold_role=["formatting", "first_editor"],
            capable_of=["ianaconsid-beginner", "xmlfmt-beginner"],
            manager=bjenkins,
        )
        RpcPersonFactory(
            datatracker_person__plain_name="O. Bleu",
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
            manager=bjenkins,
        )
        RpcPersonFactory(
            datatracker_person__plain_name="Patricia Parker",
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
            manager=bjenkins,
        )
        RpcPersonFactory(
            datatracker_person__plain_name="S. Bexar",
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
            manager=bjenkins,
        )
        RpcPersonFactory(
            datatracker_person__plain_name="T. Langfeld",
            can_hold_role=["formatting", "first_editor"],
            capable_of=["ianaconsid-beginner", "xmlfmt-beginner"],
            manager=bjenkins,
        )
        RpcPersonFactory(
            datatracker_person__plain_name="U. Garrison",
            can_hold_role=["formatting"],
            capable_of=["xmlfmt-expert"],
            manager=bjenkins,
        )

    # todo bring this to life
    def create_documents(self):
        # WgDraftFactory(states=[("draft-iesg", "pub-req")])
        #
        # # Draft sent to RPC and in progress as an RfcToBe
        # RfcToBeFactory(
        #     rfc_number=None,
        #     draft__states=[("draft-iesg", "rfcqueue")]
        # )
        #
        # # Draft published as an RFC
        # rfc_number = next_rfc_number()[0]
        # RfcToBeFactory(
        #     disposition__slug="published",
        #     rfc_number=rfc_number,
        #     draft=WgRfcFactory(alias2__name=f"rfc{rfc_number}")
        # )
        pass
