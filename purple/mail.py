# Copyright The IETF Trust 2025, All Rights Reserved
from email.utils import make_msgid

from django.conf import settings
from django.core.mail import EmailMessage as _EmailMessage
from django.core.mail import send_mail as _send_mail


def send_mail(to, subject, msg, frm=None, fail_silently=True):
    """send_mail with purple defaults

    Customizations:
      * use settings.DEFAULT_FROM_EMAIL as from address by default
    """
    if not frm:
        frm = settings.DEFAULT_FROM_EMAIL
    if isinstance(to, str):
        to = [
            to,
        ]
    _send_mail(subject, msg, frm, to, fail_silently=fail_silently)


class EmailMessage(_EmailMessage):
    """EmailMessage with purple defaults

    Customizations:
      * use settings.DEFAULT_FROM_EMAIL as from address by default
    """

    def __init__(
        self,
        subject="",
        body="",
        from_email=None,
        to=None,
        bcc=None,
        connection=None,
        attachments=None,
        headers=None,
        cc=None,
        reply_to=None,
    ):
        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL
        super().__init__(
            subject,
            body,
            from_email,
            to,
            bcc,
            connection,
            attachments,
            headers,
            cc,
            reply_to,
        )


def make_message_id():
    return make_msgid(
        domain=getattr(settings, "MESSAGE_ID_DOMAIN", None),
    )
