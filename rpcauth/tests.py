# Copyright The IETF Trust 2023, All Rights Reserved
# -*- coding: utf-8 -*-

import datetime
from unittest.mock import patch

from django.core.exceptions import SuspiciousOperation
from django.test import TestCase
from django.test.utils import override_settings

from .backends import RpcOIDCAuthBackend


class RpcOIDCAuthBackendTests(TestCase):
    @override_settings(OIDC_OP_ISSUER_ID="http://issuer.example.com/openid")
    @override_settings(OIDC_RP_CLIENT_ID="test-client-id")
    @override_settings(OIDC_RP_CLIENT_SECRET="test-client-secret")
    def setUp(self):
        self.backend = RpcOIDCAuthBackend()

    @patch("mozilla_django_oidc.auth.OIDCAuthenticationBackend.verify_token")
    def test_verify_token(self, token_mock):
        # specify payload
        token_mock.return_value = {
            "iss": "http://issuer.example.com/openid",
            "aud": "test-client-id",
            "exp": int(
                # now + 10 minutes
                datetime.datetime.now(datetime.timezone.utc).timestamp() + 600
            ),
            "sub": "test-subject-id",
        }
        fake_token = {}  # ignored by token_mock

        self.assertEqual(
            self.backend.verify_token(fake_token),
            token_mock.return_value,
        )

        # invalid issuer
        token_mock.return_value["iss"] = "http://other-issuer.example.com/openid"
        with self.assertRaises(SuspiciousOperation) as cm:
            self.backend.verify_token(fake_token)
        self.assertIn("does not match configured issuer", str(cm.exception))

        # missing issuer
        del token_mock.return_value["iss"]
        with self.assertRaises(SuspiciousOperation) as cm:
            self.backend.verify_token(fake_token)
        self.assertIn("does not match configured issuer", str(cm.exception))

        # invalid audience
        token_mock.return_value["iss"] = (
            "http://issuer.example.com/openid"  # restore valid
        )
        token_mock.return_value["aud"] = "not-the-client"
        with self.assertRaises(SuspiciousOperation) as cm:
            self.backend.verify_token(fake_token)
        self.assertIn("has invalid audience", str(cm.exception))

        token_mock.return_value["aud"] = ["test-client-id", "not-the-client"]
        with self.assertRaises(SuspiciousOperation) as cm:
            self.backend.verify_token(fake_token)
        self.assertIn("has invalid audience", str(cm.exception))

        del token_mock.return_value["aud"]
        with self.assertRaises(SuspiciousOperation) as cm:
            self.backend.verify_token(fake_token)
        self.assertIn("has invalid audience", str(cm.exception))

        # azp valid and present
        token_mock.return_value["aud"] = "test-client-id"  # restore valid
        token_mock.return_value["azp"] = "test-client-id"  # valid
        self.assertEqual(
            self.backend.verify_token(fake_token),
            token_mock.return_value,
        )

        # azp invalid
        token_mock.return_value["azp"] = "not-the-client"
        with self.assertRaises(SuspiciousOperation) as cm:
            self.backend.verify_token(fake_token)
        self.assertIn("is not our client id", str(cm.exception))

        # expired token
        del token_mock.return_value["azp"]
        original_exp = token_mock.return_value["exp"]
        token_mock.return_value["exp"] -= 610  # expired at least 10 seconds ago
        with self.assertRaises(SuspiciousOperation) as cm:
            self.backend.verify_token(fake_token)
        self.assertIn("token expired", str(cm.exception))

        # no expiration
        del token_mock.return_value["exp"]
        with self.assertRaises(SuspiciousOperation) as cm:
            self.backend.verify_token(fake_token)
        self.assertIn("has no expiration time", str(cm.exception))

        # expiration not an integer
        token_mock.return_value["exp"] = "about half past ten"
        with self.assertRaises(SuspiciousOperation) as cm:
            self.backend.verify_token(fake_token)
        self.assertIn("is not an integer", str(cm.exception))

        # no sub
        token_mock.return_value["exp"] = original_exp
        del token_mock.return_value["sub"]
        with self.assertRaises(SuspiciousOperation) as cm:
            self.backend.verify_token(fake_token)
        self.assertIn("No subject ID", str(cm.exception))

    @patch("mozilla_django_oidc.auth.OIDCAuthenticationBackend.verify_token")
    def test_verify_claims(self, token_mock):
        # first call verify_token so the backend knows the "sub" claim to expect
        token_mock.return_value = {
            "iss": "http://issuer.example.com/openid",
            "aud": "test-client-id",
            "exp": int(
                # now + 10 minutes
                datetime.datetime.now(datetime.timezone.utc).timestamp() + 600
            ),
            "sub": "test-subject-id",
        }
        fake_token = {}
        self.backend.verify_token(fake_token)

        # missing claims
        with self.assertRaises(SuspiciousOperation) as cm:
            self.assertFalse(self.backend.verify_claims({"roles": []}))
        self.assertIn("No subject ID claim", str(cm.exception))

        with self.assertRaises(SuspiciousOperation) as cm:
            self.assertFalse(
                self.backend.verify_claims({"sub": "wrong-test-client-id", "roles": []})
            )
        self.assertIn("does not match token sub", str(cm.exception))

        # bad roles, good sub
        self.assertFalse(
            self.backend.verify_claims({"sub": "test-subject-id", "roles": []})
        )
        self.assertFalse(
            self.backend.verify_claims(
                {"sub": "test-subject-id", "roles": [["auth", "ietf-llc"]]}
            )
        )
        # good roles and sub
        self.assertTrue(
            self.backend.verify_claims(
                {
                    "sub": "test-subject-id",
                    "name": "test-name",
                    "roles": [["auth", "rpc"]],
                }
            )
        )
        self.assertTrue(
            self.backend.verify_claims(
                {
                    "sub": "test-subject-id",
                    "name": "test-name",
                    "roles": [["secr", "secretariat"]],
                }
            )
        )
