# Copyright The IETF Trust 2025, All Rights Reserved
from celery import shared_task
from celery.utils.log import get_task_logger

from purple.mail import EmailMessage
from utils.task_utils import RetryTask

logger = get_task_logger(__name__)


class EmailTask(RetryTask):
    max_retries = 4 * 24 * 3  # every 15 minutes for 3 days
    # When retries run out, the admins will be emailed. There's a good chance that
    # sending that mail will fail also, but it's what we have for now.


class SendEmailError(Exception):
    pass


@shared_task(base=EmailTask, autoretry_for=(SendEmailError,))
def send_mail_task(
    subject: str,
    body: str,
    to: list[str] | tuple[str] | None,
    cc: list[str] | tuple[str] | None,
):
    email = EmailMessage(subject=subject, body=body, to=to, cc=cc)
    try:
        email.send()
    except Exception as err:
        logger.error(
            "Sending with subject '%s' failed: %s",
            subject,
            str(err),
        )
        raise SendEmailError from err
