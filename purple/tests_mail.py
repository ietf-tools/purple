# Copyright The IETF Trust 2025, All Rights Reserved

from django.core import mail
from django.test import TestCase, override_settings

from purple.mail import send_mail


class MailTests(TestCase):
    def setUp(self):
        mail.outbox = []

    def verify_email(self, to, frm, subject, msg):
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        if isinstance(to, str):
            to = [
                to,
            ]

        self.assertEqual(email.to, to)
        self.assertEqual(email.from_email, frm)
        self.assertEqual(email.subject, subject)
        self.assertEqual(email.body, msg)

    def test_send_mail_str(self):
        to = "doe@example.org"
        frm = "rana@example.org"
        subject = "GLaDOS"
        msg = "The cake is a lie!"

        send_mail(to, subject, msg, frm)
        self.verify_email(to, frm, subject, msg)

    def test_send_mail_list(self):
        to = [
            "doe@example.org",
            "joe@example.org",
        ]
        frm = "rana@example.org"
        subject = "GLaDOS"
        msg = "The cake is a lie!"

        send_mail(to, subject, msg, frm)
        self.verify_email(to, frm, subject, msg)

    @override_settings(DEFAULT_FROM_EMAIL="glados@example.org")
    def test_send_mail_no_frm(self):
        to = [
            "doe@example.org",
            "joe@example.org",
        ]
        subject = "GLaDOS"
        msg = "The cake is a lie!"

        send_mail(to, subject, msg)
        self.verify_email(to, "glados@example.org", subject, msg)
