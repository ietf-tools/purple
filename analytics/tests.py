# Copyright The IETF Trust 2026, All Rights Reserved
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from drf_spectacular.generators import SchemaGenerator

from datatracker.factories import DatatrackerPersonFactory
from rpc.factories import (
    AssignmentFactory,
    ClusterFactory,
    DispositionNameFactory,
    LabelFactory,
    RfcToBeFactory,
    RpcPersonFactory,
    RpcRoleFactory,
    SourceFormatNameFactory,
)
from rpc.models import Assignment, ClusterMember


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)
class AnalyticsApiTests(TestCase):
    def setUp(self):
        self.editor = RpcPersonFactory(
            datatracker_person=DatatrackerPersonFactory(datatracker_id=1001)
        )
        self.rpcapi = MagicMock()
        self.rpcapi.get_persons.return_value = [
            MagicMock(id=1001, plain_name="Ed Itor")
        ]

    def _get(self, path, key="analytics-token"):
        with patch("datatracker.rpcapi.get_rpcapi_client", return_value=self.rpcapi):
            return self.client.get(path, headers={"X-API-Key": key})

    def test_documents_cover_every_disposition_with_assignments(self):
        published = RfcToBeFactory(
            disposition=DispositionNameFactory(slug="published", name="Published"),
            rfc_number=9999,
            rev="07",
        )
        withdrawn = RfcToBeFactory(
            disposition=DispositionNameFactory(slug="withdrawn", name="Withdrawn")
        )
        cluster = ClusterFactory()
        ClusterMember.objects.create(cluster=cluster, doc=published.draft, order=1)
        published.labels.add(LabelFactory(slug="internal", is_public=False))
        AssignmentFactory(
            rfc_to_be=published,
            person=self.editor,
            role=RpcRoleFactory(slug="first_editor", name="First editor"),
            state=Assignment.State.DONE,
        )
        AssignmentFactory(
            rfc_to_be=published,
            person=None,
            role=RpcRoleFactory(slug="publisher", name="Publisher"),
        )

        response = self._get("/api/analytics/documents/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 2)
        documents = {doc["disposition"]: doc for doc in response.json()["results"]}
        self.assertEqual(documents.keys(), {"published", "withdrawn"})
        self.assertEqual(documents["withdrawn"]["draft_name"], withdrawn.draft.name)
        self.assertEqual(
            documents["published"],
            {
                "draft_name": published.draft.name,
                "draft_rev": "07",
                "draft_datatracker_id": published.draft.datatracker_id,
                "rfc_number": 9999,
                "disposition": "published",
                "disposition_name": "Published",
                "published_at": None,
                "source_format": "xml-v3",
                "source_format_name": published.submitted_format.name,
                "pages": published.pages,
                "cluster": cluster.number,
                "labels": ["internal"],
                "assignments": [
                    {
                        "role": "first_editor",
                        "role_name": "First editor",
                        "state": "done",
                        "staff_datatracker_id": 1001,
                        "staff_name": "Ed Itor",
                    },
                    {
                        "role": "publisher",
                        "role_name": "Publisher",
                        "state": "assigned",
                        "staff_datatracker_id": None,
                        "staff_name": None,
                    },
                ],
            },
        )

    def test_documents_are_paged_newest_first(self):
        oldest, middle, newest = RfcToBeFactory.create_batch(3)
        response = self._get("/api/analytics/documents/?limit=2")
        self.assertEqual(response.json()["count"], 3)
        self.assertEqual(
            [doc["draft_name"] for doc in response.json()["results"]],
            [newest.draft.name, middle.draft.name],
        )
        rest = self._get("/api/analytics/documents/?limit=2&offset=2").json()
        self.assertEqual(
            [doc["draft_name"] for doc in rest["results"]], [oldest.draft.name]
        )
        self.assertIsNone(rest["next"])

    def test_staff(self):
        response = self._get("/api/analytics/staff/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [{"name": "Ed Itor", "datatracker_person_id": 1001, "is_active": True}],
        )

    def test_labels_include_unused_and_non_public(self):
        LabelFactory(slug="retired", text="Retired", used=False, is_public=False)
        response = self._get("/api/analytics/labels/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            {"slug": "retired", "name": "Retired", "used": False}, response.json()
        )

    def test_source_formats(self):
        SourceFormatNameFactory(slug="nroff", name="nroff", used=False)
        response = self._get("/api/analytics/source-formats/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            {"slug": "nroff", "name": "nroff", "used": False}, response.json()
        )

    def test_roles_include_unheld_ones(self):
        RpcRoleFactory(slug="ref_checker", name="Reference Checker")
        response = self._get("/api/analytics/roles/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            {"slug": "ref_checker", "name": "Reference Checker"}, response.json()
        )

    def test_dispositions_include_ones_without_documents(self):
        DispositionNameFactory(slug="withdrawn", name="Withdrawn")
        response = self._get("/api/analytics/dispositions/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            {"slug": "withdrawn", "name": "Withdrawn", "used": True}, response.json()
        )

    def test_requires_the_analytics_key(self):
        self.assertEqual(self.client.get("/api/analytics/staff/").status_code, 403)
        self.assertEqual(
            self._get("/api/analytics/staff/", key="pubq-token").status_code, 403
        )
        self.client.force_login(
            get_user_model().objects.create_user(username="rpc-member")
        )
        self.assertEqual(self.client.get("/api/analytics/staff/").status_code, 403)

    def test_analytics_key_grants_nothing_else(self):
        for path in ("/api/rpc/rpc_person/", "/api/rpc/queue/", "/api/pubq/queue/"):
            with self.subTest(path=path):
                self.assertEqual(self._get(path).status_code, 403)

    def test_schema_covers_only_analytics(self):
        response = self._get("/api/analytics/schema/?format=json")
        self.assertEqual(response.status_code, 200)
        paths = set(response.json()["paths"])
        self.assertIn("/api/analytics/documents/", paths)
        self.assertTrue(all(p.startswith("/api/analytics/") for p in paths))
        self.assertEqual(
            self._get("/api/analytics/schema/", key="pubq-token").status_code, 403
        )

    def test_purple_schema_leaves_out_analytics(self):
        schema = SchemaGenerator().get_schema(request=None, public=True)
        self.assertIn("/api/rpc/queue/", schema["paths"])
        self.assertFalse(any(p.startswith("/api/analytics/") for p in schema["paths"]))
