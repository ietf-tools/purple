# Copyright The IETF Trust 2025, All Rights Reserved

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

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
                        help_text="ID of the Person in the datatracker", unique=True
                    ),
                ),
            ],
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
    ]
