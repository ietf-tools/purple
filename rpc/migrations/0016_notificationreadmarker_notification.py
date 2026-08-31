# Copyright The IETF Trust 2026, All Rights Reserved

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0015_backfill_refqueue_target_rfctobe"),
    ]

    operations = [
        migrations.CreateModel(
            name="NotificationReadMarker",
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
                ("seen_at", models.DateTimeField(blank=True, null=True)),
                (
                    "person",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification_read_marker",
                        to="rpc.rpcperson",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Notification",
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
                    "event_type",
                    models.CharField(
                        choices=[
                            ("blocked", "document blocked"),
                            ("unblocked", "document unblocked"),
                        ],
                        max_length=32,
                    ),
                ),
                ("data", models.JSONField(blank=True, default=dict)),
                ("created", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "recipient",
                    models.ForeignKey(
                        blank=True,
                        help_text="Person to notify; null broadcasts to everyone",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="rpc.rpcperson",
                    ),
                ),
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        blank=True,
                        help_text="Document this notification is about",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="rpc.rfctobe",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
                "indexes": [
                    models.Index(
                        fields=["recipient", "-created"],
                        name="rpc_notific_recipie_a56748_idx",
                    )
                ],
            },
        ),
    ]
