# Copyright The IETF Trust 2023, All Rights Reserved

import json
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import rpcapi_client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework.exceptions import NotFound

from datatracker.factories import DocumentFactory
from datatracker.models import Document
from rpc.models import DocRelationshipName, RpcRelatedDocument

from .api import apply_submission_cluster_membership, resolve_rfctobe
from .factories import (
    ClusterFactory,
    DispositionNameFactory,
    RfcToBeFactory,
    SourceFormatNameFactory,
    StdLevelNameFactory,
    StreamNameFactory,
    TlpBoilerplateChoiceNameFactory,
    UnusableRfcNumberFactory,
)
from .utils import next_rfc_number

# Minimal data that rpcapi_client.FullDraft.from_json() accepts


class GetRfcToBeForDraftNameTests(TestCase):
    def test_returns_match(self):
        rfctobe = RfcToBeFactory()
        result = resolve_rfctobe(rfctobe.draft.name)
        self.assertEqual(result, rfctobe)

    def test_raises_not_found_when_missing(self):
        with self.assertRaises(NotFound):
            resolve_rfctobe("draft-does-not-exist")

    def test_prefers_non_withdrawn_when_multiple(self):
        withdrawn = DispositionNameFactory(slug="withdrawn")
        active = RfcToBeFactory()
        # Create a withdrawn duplicate sharing the same draft
        RfcToBeFactory(draft=active.draft, disposition=withdrawn)
        result = resolve_rfctobe(active.draft.name)
        self.assertEqual(result, active)

    def test_falls_back_to_withdrawn_when_only_option(self):
        withdrawn = DispositionNameFactory(slug="withdrawn")
        rfctobe = RfcToBeFactory(disposition=withdrawn)
        result = resolve_rfctobe(rfctobe.draft.name)
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


@patch("rpc.serializers.compute_deep_references_task")
class RelatedDocumentClusterSyncTests(TestCase):
    def setUp(self):
        self.relationship, _ = DocRelationshipName.objects.get_or_create(
            slug="updates",
            defaults={
                "name": "Updates",
                "desc": "",
            },
        )
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="test-password",
            name="Test User",
        )
        self.client.force_login(self.user)

    def test_create_related_document_creates_new_cluster_for_source_and_target(
        self, mock_task
    ):
        ClusterFactory(number=7)
        source = RfcToBeFactory(draft__name="draft-source-doc")
        target = RfcToBeFactory(draft__name="draft-target-doc")

        response = self.client.post(
            reverse(
                "documents-related-list", kwargs={"draft_name": "draft-source-doc"}
            ),
            data=json.dumps(
                {
                    "source": source.id,
                    "relationship": "refqueue",
                    "target_draft_name": target.draft.name,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201, response.content)

        source.refresh_from_db()
        target.refresh_from_db()

        self.assertIsNotNone(source.cluster)
        self.assertEqual(source.cluster.number, 8)  # expect incremented cluster number
        self.assertEqual(target.cluster.number, source.cluster.number)

    def test_create_related_document_adds_target_to_existing_source_cluster(
        self, mock_task
    ):
        source = RfcToBeFactory(draft__name="draft-source-doc")
        target = RfcToBeFactory(draft__name="draft-target-doc")
        cluster = ClusterFactory(number=11)
        cluster.docs.add(source.draft, through_defaults={"order": 1})

        response = self.client.post(
            reverse(
                "documents-related-list", kwargs={"draft_name": "draft-source-doc"}
            ),
            data=json.dumps(
                {
                    "source": source.id,
                    "relationship": "refqueue",
                    "target_draft_name": target.draft.name,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201, response.content)

        target.refresh_from_db()
        self.assertEqual(target.cluster.number, cluster.number)


class ApplySubmissionClusterMembershipTests(TestCase):
    def test_no_refs_creates_no_cluster(self):
        doc = RfcToBeFactory().draft
        result = apply_submission_cluster_membership(
            current_doc=doc,
            reference_docs=[],
            received_reference_ids=set(),
            has_not_received_refs=False,
        )
        self.assertIsNone(result)
        self.assertFalse(doc.clustermember_set.exists())

    def test_not_received_refs_creates_cluster_for_current_doc_only(self):
        """Draft A with only not-received references gets a single-doc cluster."""
        doc_a = RfcToBeFactory().draft
        result = apply_submission_cluster_membership(
            current_doc=doc_a,
            reference_docs=[],
            received_reference_ids=set(),
            has_not_received_refs=True,
        )
        self.assertIsNotNone(result)
        self.assertEqual(list(result.docs.all()), [doc_a])

    def test_later_received_doc_joins_waiting_cluster(self):
        """Draft B, imported after A, joins A's existing cluster."""
        doc_a = RfcToBeFactory().draft
        cluster_a = apply_submission_cluster_membership(
            current_doc=doc_a,
            reference_docs=[],
            received_reference_ids=set(),
            has_not_received_refs=True,
        )

        # B is now imported; A's cluster is found via its datatracker_id
        doc_b = DocumentFactory(pages=1)
        apply_submission_cluster_membership(
            current_doc=doc_b,
            reference_docs=[doc_a],
            received_reference_ids={doc_a.datatracker_id},
        )

        doc_b.refresh_from_db()
        self.assertEqual(doc_b.clustermember_set.get().cluster, cluster_a)

    def test_current_doc_already_clustered_reference_joins_it(self):
        """If current doc is already in a cluster, unclustered references join it."""
        doc_a = RfcToBeFactory().draft
        cluster_a = apply_submission_cluster_membership(
            current_doc=doc_a,
            reference_docs=[],
            received_reference_ids=set(),
            has_not_received_refs=True,
        )

        doc_b = DocumentFactory(pages=1)
        apply_submission_cluster_membership(
            current_doc=doc_a,
            reference_docs=[doc_b],
            received_reference_ids={doc_b.datatracker_id},
        )

        doc_b.refresh_from_db()
        self.assertEqual(doc_b.clustermember_set.get().cluster, cluster_a)

    def test_later_received_doc_creates_cluster_if_source_unclustered(self):
        """If A somehow has no cluster, importing B creates one for both."""
        doc_a = RfcToBeFactory().draft
        doc_b = DocumentFactory(pages=1)

        apply_submission_cluster_membership(
            current_doc=doc_b,
            reference_docs=[doc_a],
            received_reference_ids={doc_a.datatracker_id},
        )

        doc_a.refresh_from_db()
        doc_b.refresh_from_db()
        cluster_a = doc_a.clustermember_set.get().cluster
        cluster_b = doc_b.clustermember_set.get().cluster
        self.assertEqual(cluster_a, cluster_b)

    def test_not_received_upgrade_clusters_b_with_existing_a_cluster(self):
        """Simulates the upgrade path: not-received→refqueue puts B in A's cluster."""
        not_received_rel, _ = DocRelationshipName.objects.get_or_create(
            slug="not-received", defaults={"name": "Not Received", "desc": ""}
        )
        rfctobe_a = RfcToBeFactory()
        doc_b = DocumentFactory(pages=1)

        # A has a cluster (created when A was imported with not-received ref to B)
        cluster_a = apply_submission_cluster_membership(
            current_doc=rfctobe_a.draft,
            reference_docs=[],
            received_reference_ids=set(),
            has_not_received_refs=True,
        )

        # Record the not-received relationship from A → B
        RpcRelatedDocument.objects.create(
            source=rfctobe_a,
            relationship=not_received_rel,
            target_document=doc_b,
        )

        # B is now imported: the upgrade path clusters B with A
        apply_submission_cluster_membership(
            current_doc=doc_b,
            reference_docs=[rfctobe_a.draft],
            received_reference_ids={rfctobe_a.draft.datatracker_id},
        )

        doc_b.refresh_from_db()
        self.assertEqual(doc_b.clustermember_set.get().cluster, cluster_a)


@patch("rpc.serializers.compute_deep_references_task")
@patch("rpc.api.set_stream_manager_task")
class ImportSubmissionClusteringTests(TestCase):
    """Integration tests: import_submission creates/joins clusters correctly."""

    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_user(
            username="import-cluster-user",
            password="test-password",
            name="Import Cluster User",
        )
        self.client.force_login(self.user)
        self.fmt = SourceFormatNameFactory(slug="xml-v3")
        self.boilerplate = TlpBoilerplateChoiceNameFactory(slug="trust200902")
        self.std_level = StdLevelNameFactory(slug="ps")
        self.stream = StreamNameFactory(slug="ietf")

    def _make_rpcapi(self, drafts_by_id, refs_by_id=None):
        """Return a mock rpcapi configured for the given drafts and references.

        drafts_by_id: {doc_id: draft_name}
        refs_by_id:   {doc_id: {ref_id: ref_name}} — defaults to no refs
        """
        refs_by_id = refs_by_id or {}
        mock = MagicMock()

        def _draft(doc_id, name):
            return rpcapi_client.FullDraft(
                id=doc_id,
                name=name,
                rev="00",
                title=f"Test: {name}",
                abstract="",
                group="",
                stream="ietf",
                pages=10,
                intended_std_level="",
                consensus=None,
                authors=[],
            )

        draft_map = {
            doc_id: _draft(doc_id, name) for doc_id, name in drafts_by_id.items()
        }
        mock.get_draft_by_id.side_effect = lambda doc_id: draft_map.get(doc_id)

        def _refs(doc_id):
            return [
                rpcapi_client.Reference(id=ref_id, name=ref_name)
                for ref_id, ref_name in refs_by_id.get(doc_id, {}).items()
            ]

        mock.get_draft_references.side_effect = _refs
        return mock

    def _do_import(self, document_id, rpcapi):
        data = {
            "submitted_format": self.fmt.pk,
            "boilerplate": self.boilerplate.pk,
            "std_level": self.std_level.pk,
            "stream": self.stream.pk,
            "external_deadline": (date.today() + timedelta(days=30)).isoformat(),
            "labels": [],
        }
        with patch("datatracker.rpcapi.get_rpcapi_client", return_value=rpcapi):
            return self.client.post(
                f"/api/rpc/submissions/{document_id}/import/",
                data=json.dumps(data),
                content_type="application/json",
            )

    def test_import_a_with_not_received_b_creates_cluster(self, mock_sst, mock_cdr):
        """A imported with an unreceived normative ref to B → A gets its own cluster."""
        A_ID, B_ID = 1001, 1002
        rpcapi = self._make_rpcapi(
            drafts_by_id={A_ID: "draft-cluster-a", B_ID: "draft-cluster-b"},
            refs_by_id={A_ID: {B_ID: "draft-cluster-b"}},
        )
        response = self._do_import(A_ID, rpcapi)
        self.assertEqual(response.status_code, 200, response.content)

        doc_a = Document.objects.get(datatracker_id=A_ID)
        self.assertTrue(
            doc_a.clustermember_set.exists(),
            "A should be placed in a cluster when it has a not-received reference",
        )

    def test_import_b_after_a_joins_same_cluster(self, mock_sst, mock_cdr):
        """B imported after A (which had a not-received ref to B) joins A's cluster."""
        A_ID, B_ID = 2001, 2002

        # Step 1 – import A; B is not yet in the queue
        rpcapi_a = self._make_rpcapi(
            drafts_by_id={A_ID: "draft-join-a", B_ID: "draft-join-b"},
            refs_by_id={A_ID: {B_ID: "draft-join-b"}},
        )
        resp = self._do_import(A_ID, rpcapi_a)
        self.assertEqual(resp.status_code, 200, resp.content)

        # Step 2 – import B; its own normative reference list is empty
        rpcapi_b = self._make_rpcapi(
            drafts_by_id={B_ID: "draft-join-b"},
        )
        resp = self._do_import(B_ID, rpcapi_b)
        self.assertEqual(resp.status_code, 200, resp.content)

        doc_a = Document.objects.get(datatracker_id=A_ID)
        doc_b = Document.objects.get(datatracker_id=B_ID)
        cluster_a = doc_a.clustermember_set.get().cluster
        cluster_b = doc_b.clustermember_set.get().cluster
        self.assertEqual(cluster_a, cluster_b, "A and B must be in the same cluster")


class DocumentSearchTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="search-user",
            password="test-password",
            name="Search User",
        )
        self.client.force_login(self.user)

    def test_search_filters_by_disposition(self):
        DispositionNameFactory(slug="created")
        in_progress = RfcToBeFactory(draft__name="draft-search-target-active")
        RfcToBeFactory(
            draft__name="draft-search-target-created",
            disposition=DispositionNameFactory(slug="created"),
        )

        response = self.client.get(
            reverse("rfctobe-search"),
            {"q": "draft-search-target", "disposition": "in_progress"},
        )

        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(len(payload["results"]), 1)
        self.assertEqual(payload["results"][0]["id"], in_progress.id)
        self.assertEqual(payload["results"][0]["disposition"], "in_progress")
