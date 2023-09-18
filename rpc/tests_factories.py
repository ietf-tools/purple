# Copyright The IETF Trust 2023, All Rights Reserved
# -*- coding: utf-8 -*-

from django.test import TestCase

from .factories import (
    ActionHolderFactory,
    AprilFirstRfcToBeFactory,
    AssignmentFactory,
    CapabilityFactory,
    ClusterFactory,
    DispositionNameFactory,
    FinalApprovalFactory,
    RfcAuthorFactory,
    RpcPersonFactory,
    RpcRoleFactory,
    RfcToBeFactory,
    RpcAuthorCommentFactory,
    UnusableRfcNumberFactory,
)


class BasicRpcFactoryTests(TestCase):
    def test_default_factories_dont_crash(self):
        RpcPersonFactory()
        RpcRoleFactory()
        CapabilityFactory()
        DispositionNameFactory()
        RfcToBeFactory()
        AprilFirstRfcToBeFactory()
        ActionHolderFactory()
        RpcAuthorCommentFactory()
        ClusterFactory()
        UnusableRfcNumberFactory()
        AssignmentFactory()
        RfcAuthorFactory()
        FinalApprovalFactory()


class RpcPersonFactoryTests(TestCase):
    def test_bare(self):
        p = RpcPersonFactory()
        self.assertFalse(p.can_hold_role.exists())
        self.assertFalse(p.capable_of.exists())

    def test_can_hold_role(self):
        p = RpcPersonFactory(can_hold_role=["foo", "bar"])
        self.assertCountEqual(
            p.can_hold_role.values_list("slug", flat=True), ["foo", "bar"]
        )
        roles = RpcRoleFactory.create_batch(3)
        p = RpcPersonFactory(can_hold_role=roles)
        self.assertCountEqual(p.can_hold_role.all(), roles)


class UnusableRfcNumberFactoryTests(TestCase):
    def test_get_next_number(self):
        UnusableRfcNumberFactory(number=5000000)
        r = UnusableRfcNumberFactory()
        self.assertEqual(r.number, 5000001)


class ClusterFactoryTests(TestCase):
    def test_get_next_number(self):
        ClusterFactory(number=237)
        c = ClusterFactory()
        self.assertEqual(c.number, 238)
