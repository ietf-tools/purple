# Copyright The IETF Trust 2025, All Rights Reserved

import django.db.models.deletion
from django.db import migrations, models

import purple.mail
import rpc.models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0002_initial"),
        ("rpc", "0030_add_rfctobe_repository"),
    ]

    operations = [
        migrations.CreateModel(
            name="MailMessage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "msgtype",
                    models.CharField(
                        choices=[
                            ("blank", "freeform"),
                            ("finalapproval", "final approval"),
                            ("publication", "publication announcement"),
                        ],
                        max_length=64,
                    ),
                ),
                ("to", rpc.models.AddressListField()),
                ("cc", rpc.models.AddressListField(blank=True)),
                ("subject", models.CharField()),
                ("body", models.TextField()),
                ("message_id", models.CharField(default=purple.mail.make_message_id)),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("sent", models.BooleanField(default=False)),
                (
                    "draft",
                    models.ForeignKey(
                        blank=True,
                        help_text="draft to which this message relates",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="datatracker.document",
                    ),
                ),
                (
                    "rfctobe",
                    models.ForeignKey(
                        blank=True,
                        help_text="RfcToBe to which this message relates",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rpc.rfctobe",
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="datatracker.datatrackerperson",
                    ),
                ),
            ],
        ),
    ]
