# Copyright The IETF Trust 2026, All Rights Reserved
from unittest.mock import patch

from django.test import TestCase

from rpc.factories import RfcToBeFactory, TaskRunFactory
from rpc.models import RfcToBe

from .notifications import SkippedChangeNotification, process_rfctobe_changes_for_queue


class ProcessRfctobeChangesForQueueTests(TestCase):
    def test_skips_if_running(self):
        TaskRunFactory(task_name="process_rfctobe_changes_for_queue", is_running=True)
        with self.assertRaises(SkippedChangeNotification) as cm:
            process_rfctobe_changes_for_queue()
        self.assertIn("already running", str(cm.exception))

    def test_defers_when_recent_changes(self):
        updated_rfc = RfcToBeFactory()
        with (
            patch(
                "rpc.lifecycle.notifications.get_updated_rfcs_since",
                return_value=RfcToBe.objects.filter(pk=updated_rfc.pk),
            ),
            self.assertRaises(SkippedChangeNotification) as cm,
        ):
            process_rfctobe_changes_for_queue()
        self.assertIn("Recent changes detected", str(cm.exception))
