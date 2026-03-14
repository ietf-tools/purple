# Copyright The IETF Trust 2023, All Rights Reserved

from django.test import TestCase
from rest_framework.exceptions import NotFound

from .api import get_rfctobe_for_draft_name
from .factories import DispositionNameFactory, RfcToBeFactory, UnusableRfcNumberFactory
from .utils import next_rfc_number


class GetRfcToBeForDraftNameTests(TestCase):
    def test_returns_match(self):
        rfctobe = RfcToBeFactory()
        result = get_rfctobe_for_draft_name(rfctobe.draft.name)
        self.assertEqual(result, rfctobe)

    def test_raises_not_found_when_missing(self):
        with self.assertRaises(NotFound):
            get_rfctobe_for_draft_name("draft-does-not-exist")

    def test_prefers_non_withdrawn_when_multiple(self):
        withdrawn = DispositionNameFactory(slug="withdrawn")
        active = RfcToBeFactory()
        # Create a withdrawn duplicate sharing the same draft
        RfcToBeFactory(draft=active.draft, disposition=withdrawn)
        result = get_rfctobe_for_draft_name(active.draft.name)
        self.assertEqual(result, active)

    def test_falls_back_to_withdrawn_when_only_option(self):
        withdrawn = DispositionNameFactory(slug="withdrawn")
        rfctobe = RfcToBeFactory(disposition=withdrawn)
        result = get_rfctobe_for_draft_name(rfctobe.draft.name)
        self.assertEqual(result, rfctobe)


class UtilsTests(TestCase):
    def test_next_rfc_number(self):
        self.assertEqual(next_rfc_number(), [1])
        self.assertEqual(next_rfc_number(2), [1, 2])
        self.assertEqual(next_rfc_number(5), [1, 2, 3, 4, 5])

        UnusableRfcNumberFactory(number=1)
        self.assertEqual(next_rfc_number(), [2])
        self.assertEqual(next_rfc_number(2), [2, 3])
        self.assertEqual(next_rfc_number(5), [2, 3, 4, 5, 6])

        RfcToBeFactory(rfc_number=2)
        self.assertEqual(next_rfc_number(), [3])
        self.assertEqual(next_rfc_number(2), [3, 4])
        self.assertEqual(next_rfc_number(5), [3, 4, 5, 6, 7])

        # Need the equivalent test to avoid collisions woth datatracker RFC numbers
        # DocAliasFactory(name="rfc3")
        # self.assertEqual(next_rfc_number(), [4])
        # self.assertEqual(next_rfc_number(2), [4, 5])
        # self.assertEqual(next_rfc_number(5), [4, 5, 6, 7, 8])

        # next_rfc_number is not done until this one passes!
        # UnusableRfcNumberFactory(number=6)
        # self.assertEqual(next_rfc_number(), [4])
        # self.assertEqual(next_rfc_number(2), [4, 5])
        # self.assertEqual(next_rfc_number(5), [7, 8, 9, 10, 11])
