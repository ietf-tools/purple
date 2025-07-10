# Copyright The IETF Trust 2025, All Rights Reserved

from django.conf import settings
from django.core.mail import send_mail as dj_send


def send_mail(to, subject, msg, frm=None, fail_silently=True):
    if not frm:
        frm = settings.DEFAULT_FROM_EMAIL
    if isinstance(to, str):
        to = [
            to,
        ]
    dj_send(subject, msg, frm, to, fail_silently=fail_silently)
