# Copyright The IETF Trust 2024, All Rights Reserved
"""Tests"""
from django.test import TestCase


class HealthTests(TestCase):
    """Health check tests"""

    def test_health(self):
        """health check should return a k8s-compatible status

        The test does not use the URL reverse() tool because we want to be sure that the specific
        URL path `/health/` is functioning as intended.
        """
        r = self.client.get("/health/")
        self.assertTrue(200 <= r.status_code < 400)
