# Copyright The IETF Trust 2025, All Rights Reserved
from celery import shared_task

from purple.mail import EmailMessage


@shared_task
def send_mail_task(
    subject: str,
    body: str,
    to: list[str] | tuple[str] | None,
    cc: list[str] | tuple[str] | None,
):
    email = EmailMessage(subject=subject, body=body, to=to, cc=cc)
    email.send(fail_silently=False)
