# Copyright The IETF Trust 2025, All Rights Reserved
from email.utils import formataddr
from textwrap import dedent

from celery import Task, shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

from datatracker.utils.publication import PublicationError, publish_rfc
from purple.mail import send_mail
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
            f"Emailing admins to report failure: {self.name}[{task_id}] "
            f"with args={args} and kwargs={kwargs}. Giving up after "
            f"{self.request.retries} retries."
        )
        send_mail(
            to=[formataddr(admin) for admin in settings.ADMINS],
            subject=f"Purple task failed: {self.name}[{task_id}]",
            msg=dedent(f"""\
                Purple datatracker notification task {self.name} failed!

                Giving up after {self.request.retries} attempts.

                Task name: {self.name}
                Task id: {task_id}
                Task args: {args}
                Task kwargs: {kwargs}
                Exception: {repr(exc)}

            """)
            + str(einfo),
        )


@shared_task(
    bind=True,
    base=DatatrackerNotificationTask,
    throws=(RfcToBe.DoesNotExist, PublicationError),
    autoretry_for=(Exception,),
    dont_autoretry_for=(RfcToBe.DoesNotExist, PublicationError),
)
def notify_rfc_published_task(self, rfctobe_id):
    rfctobe = RfcToBe.objects.get(pk=rfctobe_id)
    publish_rfc(rfctobe)
