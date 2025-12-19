# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models

import purple.mail
import rpc.models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0029_historicalrfctobeblockingreason_and_more"),
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
            ],
        ),
    ]
