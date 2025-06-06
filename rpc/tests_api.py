# Copyright The IETF Trust 2025, All Rights Reserved

import json

from django.test import Client, TestCase
from django.test.utils import override_settings


class ApiTests(TestCase):
    @override_settings(
        APP_API_TOKENS={
            "purple.api.merge_person": ["valid-token"],
        }
    )
    def test_merge_person(self):
        url = "/api/merge_person/"
        client = Client()
        data = {"old_person_id": 12, "new_person_id": 13}
        headers_valid = {"X_API_KEY": "valid-token"}
        headers_invalid = {"X_API_KEY": "INVALID-TOKEN"}

        # POST: without an API token
        response = client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

        # POST: invalid token
        response = client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            headers=headers_invalid,
        )
        self.assertEqual(response.status_code, 403)

        # POST: valid token with no data
        response = client.post(url, headers=headers_valid)

        # POST: valid token with incomplete data
        incomplete_data = {"old_person_id": 12}
        response = client.post(
            url,
            data=json.dumps(incomplete_data),
            content_type="application/json",
            headers=headers_valid,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("This field is required.", response.json()["new_person_id"])

        # POST: valid token with incomplete data
        incomplete_data = {"new_person_id": 12}
        response = client.post(
            url,
            data=json.dumps(incomplete_data),
            content_type="application/json",
            headers=headers_valid,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("This field is required.", response.json()["old_person_id"])

        ## POST valid request and token
        response = client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            headers=headers_valid,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

        # GET: valid token
        response = client.get(url, headers={"X_API_KEY": "valid-token"})
        self.assertEqual(response.status_code, 405)

        # GET: invalid token
        response = client.get(url, headers={"X_API_KEY": "invalid-token"})
        self.assertEqual(response.status_code, 403)
