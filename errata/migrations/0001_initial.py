# Copyright The IETF Trust 2025, All Rights Reserved

import django.contrib.postgres.fields
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import errata.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("datatracker", "0001_initial"),
        ("rpc", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Status",
            fields=[
                (
                    "slug",
                    models.CharField(max_length=32, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=255)),
                ("desc", models.TextField(blank=True)),
                ("used", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name_plural": "Statuses",
            },
        ),
        migrations.CreateModel(
            name="Type",
            fields=[
                (
                    "slug",
                    models.CharField(max_length=32, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=255)),
                ("desc", models.TextField(blank=True)),
                ("used", models.BooleanField(default=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Errata",
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
                ("section", models.TextField(blank=True)),
                ("orig_text", models.TextField(blank=True)),
                ("corrected_text", models.TextField(blank=True)),
                ("submitter_name", models.CharField(blank=True, max_length=80)),
                ("submitter_email", models.EmailField(blank=True, max_length=120)),
                ("notes", models.TextField(blank=True)),
                ("submitted_at", models.DateField()),
                ("posted_at", models.DateField(null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", errata.models.AutoDateTimeField()),
                (
                    "format",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[("HTML", "HTML"), ("PDF", "PDF"), ("TXT", "TXT")],
                            max_length=10,
                        ),
                        blank=True,
                        default=list,
                        help_text=(
                            "A list of formats. Possible values: 'HTML', 'PDF', "
                            "and 'TXT'."
                        ),
                        size=None,
                    ),
                ),
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="errata",
                        to="rpc.rfctobe",
                    ),
                ),
                (
                    "submitter_dt_person",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="errata_submitter_dt_person",
                        to="datatracker.datatrackerperson",
                    ),
                ),
                (
                    "verifier_dt_person",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="errata_verifier_dt_person",
                        to="datatracker.datatrackerperson",
                    ),
                ),
                (
                    "status",
                    models.ForeignKey(
                        db_column="status_slug",
                        default="reported",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="errata",
                        to="errata.status",
                    ),
                ),
                (
                    "type",
                    models.ForeignKey(
                        blank=True,
                        db_column="type_slug",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="errata",
                        to="errata.type",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Errata",
            },
        ),
        migrations.CreateModel(
            name="Log",
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
                ("section", models.TextField(blank=True)),
                ("orig_text", models.TextField(blank=True)),
                ("corrected_text", models.TextField(blank=True)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "editor_dt_person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="logs_editor_dt_person",
                        to="datatracker.datatrackerperson",
                    ),
                ),
                (
                    "errata",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="logs_errata",
                        to="errata.errata",
                    ),
                ),
                (
                    "verifier_dt_person",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="logs_verifier_dt_person",
                        to="datatracker.datatrackerperson",
                    ),
                ),
                (
                    "status",
                    models.ForeignKey(
                        db_column="status_slug",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="logs_status",
                        to="errata.status",
                    ),
                ),
                (
                    "type",
                    models.ForeignKey(
                        db_column="type_slug",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="logs_type",
                        to="errata.type",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AreaAssignment",
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
                ("area_acronym", models.CharField(max_length=32)),
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="area_assignment_rfc_to_be",
                        to="rpc.rfctobe",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("rfc_to_be", "area_acronym"),
                        name="unique_rfc_to_be_area_acronym",
                    )
                ],
            },
        ),
    ]
