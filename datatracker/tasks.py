# Copyright The IETF Trust 2025, All Rights Reserved
from celery import Task, shared_task
from celery.utils.log import get_task_logger

from datatracker.utils.publication import publish_rfc
from rpc.models import RfcToBe

logger = get_task_logger(__name__)


class DatatrackerNotificationTask(Task):
    max_retries = 4 * 24 * 7  # every 15 minutes for a week
    acks_late = True  # task is idempotent; prefer duplicated to lost attempts

    retry_delay_schedule = [3, 3, 6, 10, 15, 30, 60, 120, 240, 480, 900]

    def _retry_delay(self, n):
        if n < len(self.retry_delay_schedule):
            return self.retry_delay_schedule[n]
        return self.retry_delay_schedule[-1]

    def retry(
        self,
        args=None,
        kwargs=None,
        exc=None,
        throw=True,
        eta=None,
        countdown=None,
        max_retries=None,
        **options,
    ):
        if countdown is None:
            countdown = self._retry_delay(self.request.retries)
        super().retry(args, kwargs, exc, throw, eta, countdown, max_retries, **options)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(
            f"Email admins to report failure: {self.name} "
            f"with args={args} and kwargs={kwargs}"
        )


@shared_task(
    bind=True,
    base=DatatrackerNotificationTask,
    throws=(RfcToBe.DoesNotExist,),
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2},
)
def notify_rfc_published_task(self, rfctobe_id):
    rfctobe = RfcToBe.objects.get(pk=rfctobe_id)
    publish_rfc(rfctobe)
