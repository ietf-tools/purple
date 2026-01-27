# Copyright The IETF Trust 2025-2026, All Rights Reserved

import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DatatrackerPerson",
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
                    "datatracker_id",
                    models.BigIntegerField(
                        help_text="ID of the Person in the datatracker"
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="Document",
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
                ("datatracker_id", models.BigIntegerField(unique=True)),
                (
                    "name",
                    models.CharField(
                        help_text="Name of draft", max_length=255, unique=True
                    ),
                ),
                ("rev", models.CharField(help_text="Revision of draft", max_length=16)),
                ("title", models.CharField(help_text="Title of draft", max_length=255)),
                (
                    "stream",
                    models.CharField(help_text="Stream of draft", max_length=32),
                ),
                (
                    "pages",
                    models.PositiveSmallIntegerField(help_text="Number of pages"),
                ),
                ("intended_std_level", models.CharField(blank=True, max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name="DocumentLabel",
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
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="datatracker.document",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HistoricalDatatrackerPerson",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "datatracker_id",
                    models.BigIntegerField(
                        help_text="ID of the Person in the datatracker"
                    ),
                ),
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
                "verbose_name": "historical datatracker person",
                "verbose_name_plural": "historical datatracker persons",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
