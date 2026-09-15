# Copyright The IETF Trust 2026, All Rights Reserved
"""Test runner that shows log output only for failing tests"""

import logging
import sys

from django.test.runner import DiscoverRunner


class _SysStream:
    """Resolve sys.stdout/sys.stderr on every write so buffer mode can swap them."""

    def __init__(self, name):
        self._name = name

    def write(self, s):
        return getattr(sys, self._name).write(s)

    def flush(self):
        getattr(sys, self._name).flush()


class QuietLogsRunner(DiscoverRunner):
    """Buffer per-test output, printing it only under failures; --show-logs shows all.

    StreamHandler binds its stream at logging setup, before unittest's buffering
    replaces sys.stderr, so console handlers are re-pointed at a lazy proxy.
    """

    def __init__(self, *, show_logs=False, **kwargs):
        if not show_logs:
            kwargs["buffer"] = True
        super().__init__(**kwargs)
        self.show_logs = show_logs

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--show-logs",
            action="store_true",
            help="Print log output from every test, not just failing ones.",
        )

    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        if self.show_logs:
            return
        for logger in (logging.root, *logging.root.manager.loggerDict.values()):
            for handler in getattr(logger, "handlers", ()):
                stream = getattr(handler, "stream", None)
                if stream is sys.stderr:
                    handler.setStream(_SysStream("stderr"))
                elif stream is sys.stdout:
                    handler.setStream(_SysStream("stdout"))
