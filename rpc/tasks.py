# Copyright The IETF Trust 2025, All Rights Reserved
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db.models import F

from rpc.models import MailMessage
from utils.task_utils import RetryTask

logger = get_task_logger(__name__)


class EmailTask(RetryTask):
    max_retries = 4 * 24 * 3  # every 15 minutes for 3 days
    # When retries run out, the admins will be emailed. There's a good chance that
    # sending that mail will fail also, but it's what we have for now.


class SendEmailError(Exception):
    pass


@shared_task(base=EmailTask, autoretry_for=(SendEmailError,))
def send_mail_task(message_id):
    message = MailMessage.objects.get(pk=message_id)
    email = message.as_emailmessage()
    try:
        email.send()
    except Exception as err:
        MailMessage.objects.filter(pk=message_id).update(attempts=F("attempts") + 1)
        logger.error(
            "Sending with subject '%s' failed: %s",
            message.subject,
            str(err),
        )
        raise SendEmailError from err
    comment = f"Sent {message.msgtype} email with Message-ID={message.message_id}"
    if message.rfctobe is not None:
        message.rfctobe.rpcdocumentcomment_set.create(
            comment=comment,
            by=message.sender,
        )
    if message.draft is not None:
        message.draft.rpcdocumentcomment_set.create(
            comment=comment,
            by=message.sender,
        )
    message.delete()
