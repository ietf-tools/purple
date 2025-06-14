# Copyright The IETF Trust 2025, All Rights Reserved

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0002_initial"),
        ("rpc", "0004_populate_capability"),
    ]

    operations = [
        migrations.CreateModel(
            name="ApprovalLogMessage",
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
                ("log_message", models.TextField()),
                ("time", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="approvallogmessage_by",
                        to="datatracker.datatrackerperson",
                    ),
                ),
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="rpc.rfctobe"
                    ),
                ),
            ],
        ),
    ]
