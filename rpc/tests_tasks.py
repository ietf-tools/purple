# Copyright The IETF Trust 2026, All Rights Reserved
from unittest.mock import patch

from django.test import TestCase

from rpc.lifecycle.notifications import SkippedChangeNotification
from rpc.tasks import process_rfctobe_changes_for_queue_task


class ProcessRfctobeChangesForQueueTaskTests(TestCase):
    def test_reports_skipped_notification(self):
        with patch(
            "rpc.tasks.process_rfctobe_changes_for_queue",
            side_effect=SkippedChangeNotification("mock skip msg"),
        ):
            retval = process_rfctobe_changes_for_queue_task()
        self.assertIn("Queue change processing skipped", retval)
        self.assertIn("mock skip msg", retval)
