# Copyright The IETF Trust 2026, All Rights Reserved

import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0002_initial"),
        ("rpc", "0011_historicalactionholder_historicalrpcauthorcomment_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalDocument",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("datatracker_id", models.BigIntegerField(db_index=True)),
                (
                    "name",
                    models.CharField(
                        db_index=True, help_text="Name of draft", max_length=255
                    ),
                ),
                ("rev", models.CharField(help_text="Revision of draft", max_length=16)),
                ("title", models.CharField(help_text="Title of draft", max_length=255)),
                (
                    "stream",
                    models.CharField(help_text="Stream of draft", max_length=32),
                ),
                (
                    "group",
                    models.CharField(
                        blank=True, help_text="Group of draft", max_length=40
                    ),
                ),
                (
                    "pages",
                    models.PositiveSmallIntegerField(help_text="Number of pages"),
                ),
                ("intended_std_level", models.CharField(blank=True, max_length=32)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical document",
                "verbose_name_plural": "historical documents",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalDocumentLabel",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("m2m_history_id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "document",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="datatracker.document",
                    ),
                ),
                (
                    "history",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="datatracker.historicaldocument",
                    ),
                ),
                (
                    "label",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.label",
                    ),
                ),
            ],
            options={
                "verbose_name": "HistoricalDocumentLabel",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
