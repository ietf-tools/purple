# Copyright The IETF Trust 2025, All Rights Reserved

from django.test import TestCase, RequestFactory
from django.test.utils import override_settings

from utils.api import is_valid_token, requires_api_token


class ApiTests(TestCase):
    @override_settings(
        APP_API_TOKENS={
            "purple.api.foobar": ["valid-token"],
            "purple.api.misconfigured": "valid-token",  # misconfigured
        }
    )
    def test_is_valid_token(self):
        self.assertFalse(is_valid_token("purple.fake.endpoint", "valid-token"))
        self.assertFalse(is_valid_token("purple.api.foobar", "invalid-token"))
        self.assertFalse(is_valid_token("purple.api.foobar", None))
        self.assertTrue(is_valid_token("purple.api.foobar", "valid-token"))

        # misconfiguration
        self.assertFalse(is_valid_token("purple.api.misconfigured", "v"))
        self.assertFalse(is_valid_token("purple.api.misconfigured", None))
        self.assertTrue(is_valid_token("purple.api.misconfigured", "valid-token"))

    @override_settings(
        APP_API_TOKENS={
            "purple.api.foo": ["valid-token"],
            "purple.api.bar": ["another-token"],
            "purple.api.misconfigured": "valid-token",  # misconfigured
        }
    )
    def test_requires_api_token(self):
        @requires_api_token("purple.api.foo")
        def protected_function(request):
            return f"Access granted: {request.method}"

        # request with a valid token
        request = RequestFactory().get(
            "/some/url", headers={"X_API_KEY": "valid-token"}
        )
        result = protected_function(request)
        self.assertEqual(result, "Access granted: GET")

        # request with an invalid token
        request = RequestFactory().get(
            "/some/url", headers={"X_API_KEY": "invalid-token"}
        )
        result = protected_function(request)
        self.assertEqual(result.status_code, 403)

        # request without a token
        request = RequestFactory().get("/some/url", headers={"X_API_KEY": ""})
        result = protected_function(request)
        self.assertEqual(result.status_code, 403)

        # request with a valid token for another API endpoint
        request = RequestFactory().get(
            "/some/url", headers={"X_API_KEY": "another-token"}
        )
        result = protected_function(request)
        self.assertEqual(result.status_code, 403)

        # requests for a misconfigured endpoint
        @requires_api_token("purple.api.misconfigured")
        def another_protected_function(request):
            return f"Access granted: {request.method}"

        # request with valid token
        request = RequestFactory().get(
            "/some/url", headers={"X_API_KEY": "valid-token"}
        )
        result = another_protected_function(request)
        self.assertEqual(result, "Access granted: GET")

        # request with invalid token with the correct initial character
        request = RequestFactory().get("/some/url", headers={"X_API_KEY": "v"})
        result = another_protected_function(request)
        self.assertEqual(result.status_code, 403)
