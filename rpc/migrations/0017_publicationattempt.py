# Copyright The IETF Trust 2026, All Rights Reserved

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0016_unique_active_rfctobe_per_draft"),
    ]

    operations = [
        migrations.CreateModel(
            name="PublicationAttempt",
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
                ("started_at", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("failed", "Failed")],
                        default="pending",
                        help_text="Record of an RFC publication request",
                    ),
                ),
                ("detail", models.CharField(blank=True, max_length=1000)),
                (
                    "rfc_to_be",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT, to="rpc.rfctobe"
                    ),
                ),
            ],
        ),
    ]
