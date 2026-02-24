# Copyright The IETF Trust 2025, All Rights Reserved
import os

from celery import Celery
from celery import signals as celery_signals
from django.conf import settings


# Disable celery's internal logging configuration, we set it up via Django
@celery_signals.setup_logging.connect
def on_setup_logging(**kwargs):
    pass


# Set the default Django settings module for the 'celery' program
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "purple.settings")

app = Celery("purple")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(ignore_result=True)
def debug_task():
    import datetime
    from sys import stdout

    stdout.write(
        f"debug_task executed at {datetime.datetime.now(tz=datetime.UTC).isoformat()}\n"
    )
    stdout.flush()


@app.task(ignore_result=True)
def debug_log_task():
    import datetime

    from celery.utils.log import get_task_logger

    get_task_logger(__name__).info(
        "debug_log_task executed at "
        + datetime.datetime.now(tz=datetime.UTC).isoformat()
    )


# Celery Beat schedule for periodic tasks
_process_rfctobe_changes_schedule = getattr(
    settings, "CELERY_PROCESS_RFCTOBE_CHANGES_SCHEDULE", 300.0
)

app.conf.beat_schedule = {
    "process-rfctobe-changes-every-minute": {
        "task": "rpc.tasks.process_rfctobe_changes_from_history",
        "schedule": _process_rfctobe_changes_schedule,
        "options": {
            # Set expires less than the schedule to prevent overlapping runs
            "expires": _process_rfctobe_changes_schedule - 5,
        },
    },
}
app.conf.timezone = "UTC"
