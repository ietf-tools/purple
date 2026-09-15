# Copyright The IETF Trust 2026, All Rights Reserved

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0003_historicaldocument_historicaldocumentlabel"),
        ("rpc", "0017_notificationreadmarker_notification"),
    ]

    operations = [
        migrations.CreateModel(
            name="EditorialNote",
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
                ("text", models.TextField(blank=True, default="")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "rfc_to_be",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="editorial_note",
                        to="rpc.rfctobe",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="datatracker.datatrackerperson",
                    ),
                ),
            ],
        ),
    ]
