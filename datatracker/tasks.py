# Copyright The IETF Trust 2025, All Rights Reserved
from celery import Task, shared_task
from celery.exceptions import MaxRetriesExceededError
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class DatatrackerNotificationTask(Task):
    max_retries = 4 * 24 * 7  # every 15 minutes for a week
    acks_late = True  # task is idempotent; prefer duplicated to lost attempts
    throws = (MaxRetriesExceededError,)

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


@shared_task(bind=True, base=DatatrackerNotificationTask)
def notify_task(self, message):
    try:
        logger.info(f"Delivering a notice to datatracker: {message}")
        raise RuntimeError("oops!")
    except RuntimeError:
        self.retry(max_retries=5)  # limit retries for proof of concept
