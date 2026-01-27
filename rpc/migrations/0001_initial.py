# Copyright The IETF Trust 2025-2026, All Rights Reserved

import datetime

import django.db.models.constraints
import django.db.models.deletion
import django.utils.timezone
import rules.contrib.models
import simple_history.models
from django.conf import settings
from django.db import migrations, models

import purple.mail
import rpc.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("datatracker", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BlockingReason",
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
            name="Capability",
            fields=[
                (
                    "slug",
                    models.CharField(max_length=32, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=255)),
                ("desc", models.TextField(blank=True)),
            ],
            options={
                "verbose_name_plural": "capabilities",
            },
        ),
        migrations.CreateModel(
            name="Cluster",
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
                ("number", models.PositiveIntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="DispositionName",
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
            name="DocRelationshipName",
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
            name="DumpInfo",
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
                ("timestamp", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="Label",
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
                ("slug", models.CharField(max_length=64, unique=True)),
                ("is_exception", models.BooleanField(default=False)),
                ("is_complexity", models.BooleanField(default=False)),
                (
                    "color",
                    models.CharField(
                        choices=[
                            ("slate", "slate"),
                            ("gray", "gray"),
                            ("zinc", "zinc"),
                            ("neutral", "neutral"),
                            ("stone", "stone"),
                            ("red", "red"),
                            ("orange", "orange"),
                            ("amber", "amber"),
                            ("yellow", "yellow"),
                            ("lime", "lime"),
                            ("green", "green"),
                            ("emerald", "emerald"),
                            ("teal", "teal"),
                            ("cyan", "cyan"),
                            ("sky", "sky"),
                            ("blue", "blue"),
                            ("indigo", "indigo"),
                            ("violet", "violet"),
                            ("purple", "purple"),
                            ("fuchsia", "fuchsia"),
                            ("pink", "pink"),
                            ("rose", "rose"),
                        ],
                        default="purple",
                        max_length=7,
                    ),
                ),
                ("used", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="RpcRole",
            fields=[
                (
                    "slug",
                    models.CharField(max_length=32, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=255)),
                ("desc", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="SourceFormatName",
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
            name="StdLevelName",
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
            name="StreamName",
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
            name="SubseriesTypeName",
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
            name="TlpBoilerplateChoiceName",
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
            name="UnusableRfcNumber",
            fields=[
                (
                    "number",
                    models.PositiveIntegerField(primary_key=True, serialize=False),
                ),
                ("comment", models.TextField(blank=True)),
            ],
            options={
                "ordering": ["number"],
            },
        ),
        migrations.CreateModel(
            name="ClusterMember",
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
                ("order", models.IntegerField()),
                (
                    "cluster",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="rpc.cluster"
                    ),
                ),
                (
                    "doc",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="datatracker.document",
                    ),
                ),
            ],
            options={
                "ordering": ["order"],
            },
        ),
        migrations.AddField(
            model_name="cluster",
            name="docs",
            field=models.ManyToManyField(
                through="rpc.ClusterMember", to="datatracker.document"
            ),
        ),
        migrations.CreateModel(
            name="HistoricalCluster",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("number", models.PositiveIntegerField(db_index=True)),
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
                "verbose_name": "historical cluster",
                "verbose_name_plural": "historical clusters",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalClusterMember",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("order", models.IntegerField()),
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
                    "cluster",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.cluster",
                    ),
                ),
                (
                    "doc",
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
                "verbose_name": "historical cluster member",
                "verbose_name_plural": "historical cluster members",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalLabel",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("slug", models.CharField(db_index=True, max_length=64)),
                ("is_exception", models.BooleanField(default=False)),
                ("is_complexity", models.BooleanField(default=False)),
                (
                    "color",
                    models.CharField(
                        choices=[
                            ("slate", "slate"),
                            ("gray", "gray"),
                            ("zinc", "zinc"),
                            ("neutral", "neutral"),
                            ("stone", "stone"),
                            ("red", "red"),
                            ("orange", "orange"),
                            ("amber", "amber"),
                            ("yellow", "yellow"),
                            ("lime", "lime"),
                            ("green", "green"),
                            ("emerald", "emerald"),
                            ("teal", "teal"),
                            ("cyan", "cyan"),
                            ("sky", "sky"),
                            ("blue", "blue"),
                            ("indigo", "indigo"),
                            ("violet", "violet"),
                            ("purple", "purple"),
                            ("fuchsia", "fuchsia"),
                            ("pink", "pink"),
                            ("rose", "rose"),
                        ],
                        default="purple",
                        max_length=7,
                    ),
                ),
                ("used", models.BooleanField(default=True)),
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
                "verbose_name": "historical label",
                "verbose_name_plural": "historical labels",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalRfcToBe",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("is_april_first_rfc", models.BooleanField(default=False)),
                (
                    "rfc_number",
                    models.PositiveIntegerField(
                        blank=True,
                        db_index=True,
                        null=True,
                        validators=[rpc.models.validate_not_unusable_rfc_number],
                    ),
                ),
                ("title", models.CharField(help_text="Document title", max_length=255)),
                (
                    "abstract",
                    models.TextField(
                        blank=True, help_text="Document abstract", max_length=32000
                    ),
                ),
                (
                    "group",
                    models.CharField(
                        blank=True,
                        help_text=(
                            "Acronym of datatracker group where this document "
                            "originated, if any"
                        ),
                        max_length=40,
                    ),
                ),
                (
                    "pages",
                    models.PositiveIntegerField(help_text="Page count", null=True),
                ),
                (
                    "keywords",
                    models.CharField(
                        blank=True,
                        help_text="Comma-separated list of keywords",
                        max_length=1000,
                    ),
                ),
                ("external_deadline", models.DateTimeField(blank=True, null=True)),
                ("internal_goal", models.DateTimeField(blank=True, null=True)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                (
                    "iana_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("no_actions", "This document has no IANA actions"),
                            (
                                "not_completed",
                                "IANA has not completed actions in draft",
                            ),
                            ("completed", "IANA has completed actions in draft"),
                            (
                                "changes_required",
                                "Changes to registries are required due to RFC edits",
                            ),
                            (
                                "reconciled",
                                "IANA has reconciled changes between draft and RFC",
                            ),
                        ],
                        default="not_completed",
                        help_text="Current status of IANA actions for this document",
                        max_length=32,
                        null=True,
                    ),
                ),
                (
                    "repository",
                    models.CharField(
                        blank=True,
                        help_text="Repository name (e.g., ietf-tools/purple)",
                        max_length=1000,
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
                    "disposition",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.dispositionname",
                    ),
                ),
                (
                    "draft",
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
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "iesg_contact",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        help_text="Responsible or shepherding AD, if any",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="datatracker.datatrackerperson",
                    ),
                ),
                (
                    "shepherd",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        help_text="Document shepherd",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="datatracker.datatrackerperson",
                    ),
                ),
                (
                    "submitted_format",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.sourceformatname",
                    ),
                ),
                (
                    "publication_std_level",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        help_text="StdLevel at publication (blank until published)",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.stdlevelname",
                    ),
                ),
                (
                    "std_level",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        help_text="Current StdLevel",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.stdlevelname",
                    ),
                ),
                (
                    "publication_stream",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        help_text="Stream at publication (blank until published)",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.streamname",
                    ),
                ),
                (
                    "stream",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        help_text="Current stream",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.streamname",
                    ),
                ),
                (
                    "boilerplate",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        help_text="TLP IPR boilerplate option",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.tlpboilerplatechoicename",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical rfc to be",
                "verbose_name_plural": "historical RfcToBes",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalUnusableRfcNumber",
            fields=[
                ("number", models.PositiveIntegerField(db_index=True)),
                ("comment", models.TextField(blank=True)),
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
                "verbose_name": "historical unusable rfc number",
                "verbose_name_plural": "historical unusable rfc numbers",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="RfcToBe",
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
                ("is_april_first_rfc", models.BooleanField(default=False)),
                (
                    "rfc_number",
                    models.PositiveIntegerField(
                        blank=True,
                        null=True,
                        unique=True,
                        validators=[rpc.models.validate_not_unusable_rfc_number],
                    ),
                ),
                ("title", models.CharField(help_text="Document title", max_length=255)),
                (
                    "abstract",
                    models.TextField(
                        blank=True, help_text="Document abstract", max_length=32000
                    ),
                ),
                (
                    "group",
                    models.CharField(
                        blank=True,
                        help_text=(
                            "Acronym of datatracker group where this document "
                            "originated, if any"
                        ),
                        max_length=40,
                    ),
                ),
                (
                    "pages",
                    models.PositiveIntegerField(help_text="Page count", null=True),
                ),
                (
                    "keywords",
                    models.CharField(
                        blank=True,
                        help_text="Comma-separated list of keywords",
                        max_length=1000,
                    ),
                ),
                ("external_deadline", models.DateTimeField(blank=True, null=True)),
                ("internal_goal", models.DateTimeField(blank=True, null=True)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                (
                    "iana_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("no_actions", "This document has no IANA actions"),
                            (
                                "not_completed",
                                "IANA has not completed actions in draft",
                            ),
                            ("completed", "IANA has completed actions in draft"),
                            (
                                "changes_required",
                                "Changes to registries are required due to RFC edits",
                            ),
                            (
                                "reconciled",
                                "IANA has reconciled changes between draft and RFC",
                            ),
                        ],
                        default="not_completed",
                        help_text="Current status of IANA actions for this document",
                        max_length=32,
                        null=True,
                    ),
                ),
                (
                    "repository",
                    models.CharField(
                        blank=True,
                        help_text="Repository name (e.g., ietf-tools/purple)",
                        max_length=1000,
                    ),
                ),
                (
                    "disposition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rpc.dispositionname",
                    ),
                ),
                (
                    "draft",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="datatracker.document",
                    ),
                ),
                (
                    "iesg_contact",
                    models.ForeignKey(
                        blank=True,
                        help_text="Responsible or shepherding AD, if any",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="datatracker.datatrackerperson",
                    ),
                ),
                (
                    "shepherd",
                    models.ForeignKey(
                        blank=True,
                        help_text="Document shepherd",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="shepherded_rfctobe_set",
                        to="datatracker.datatrackerperson",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "RfcToBes",
            },
        ),
        migrations.CreateModel(
            name="RfcAuthor",
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
                ("titlepage_name", models.CharField(max_length=128)),
                ("is_editor", models.BooleanField(default=False)),
                (
                    "order",
                    models.PositiveIntegerField(
                        help_text="Order of the author on the document"
                    ),
                ),
                (
                    "affiliation",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "datatracker_person",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="datatracker.datatrackerperson",
                    ),
                ),
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="authors",
                        to="rpc.rfctobe",
                    ),
                ),
            ],
            options={
                "ordering": ["rfc_to_be", "order"],
            },
        ),
        migrations.CreateModel(
            name="MetadataValidationResults",
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
                ("received_at", models.DateTimeField(auto_now_add=True)),
                (
                    "head_sha",
                    models.CharField(
                        blank=True,
                        help_text="Head SHA of the commit that was validated",
                        max_length=40,
                        null=True,
                    ),
                ),
                ("metadata", models.JSONField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("success", "Success"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("detail", models.TextField(blank=True, null=True)),
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="rpc.rfctobe"
                    ),
                ),
            ],
            options={
                "ordering": ["-received_at"],
            },
        ),
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
                ("to", rpc.models.AddressListField(max_length=1000)),
                ("cc", rpc.models.AddressListField(blank=True, max_length=1000)),
                ("subject", models.CharField(max_length=1000)),
                ("body", models.TextField()),
                (
                    "message_id",
                    models.CharField(
                        default=purple.mail.make_message_id, max_length=255
                    ),
                ),
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
                    "sender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="datatracker.datatrackerperson",
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
            ],
        ),
        migrations.CreateModel(
            name="HistoricalRpcDocumentComment",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("comment", models.TextField()),
                ("time", models.DateTimeField(default=django.utils.timezone.now)),
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
                    "by",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="datatracker.datatrackerperson",
                    ),
                ),
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
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.rfctobe",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical rpc document comment",
                "verbose_name_plural": "historical rpc document comments",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalRfcToBeLabel",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("m2m_history_id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "history",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="rpc.historicalrfctobe",
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
                (
                    "rfctobe",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.rfctobe",
                    ),
                ),
            ],
            options={
                "verbose_name": "HistoricalRfcToBeLabel",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalRfcToBeBlockingReason",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("since_when", models.DateTimeField(default=django.utils.timezone.now)),
                ("resolved", models.DateTimeField(blank=True, null=True)),
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
                (
                    "reason",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.blockingreason",
                    ),
                ),
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.rfctobe",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical rfc to be blocking reason",
                "verbose_name_plural": "historical rfc to be blocking reasons",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalFinalApproval",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("requested", models.DateTimeField(default=django.utils.timezone.now)),
                ("approved", models.DateTimeField(blank=True, null=True)),
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
                    "approver",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="datatracker.datatrackerperson",
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
                (
                    "overriding_approver",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="datatracker.datatrackerperson",
                    ),
                ),
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.rfctobe",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical final approval",
                "verbose_name_plural": "historical final approvals",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalApprovalLogMessage",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("log_message", models.TextField()),
                ("time", models.DateTimeField(default=django.utils.timezone.now)),
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
                    "by",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="datatracker.datatrackerperson",
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
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.rfctobe",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical approval log message",
                "verbose_name_plural": "historical approval log messages",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="FinalApproval",
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
                ("requested", models.DateTimeField(default=django.utils.timezone.now)),
                ("approved", models.DateTimeField(blank=True, null=True)),
                (
                    "approver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="approver_set",
                        to="datatracker.datatrackerperson",
                    ),
                ),
                (
                    "overriding_approver",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="overriding_approver_set",
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
        migrations.CreateModel(
            name="AdditionalEmail",
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
                ("email", models.EmailField(max_length=254)),
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="rpc.rfctobe"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ActionHolder",
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
                ("body", models.CharField(blank=True, default="", max_length=64)),
                ("since_when", models.DateTimeField(default=django.utils.timezone.now)),
                ("completed", models.DateTimeField(blank=True, null=True)),
                ("deadline", models.DateTimeField(blank=True, null=True)),
                ("comment", models.TextField(blank=True)),
                (
                    "datatracker_person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="datatracker.datatrackerperson",
                    ),
                ),
                (
                    "target_document",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="actionholder_set",
                        to="datatracker.document",
                    ),
                ),
                (
                    "target_rfctobe",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="actionholder_set",
                        to="rpc.rfctobe",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RfcToBeBlockingReason",
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
                ("since_when", models.DateTimeField(default=django.utils.timezone.now)),
                ("resolved", models.DateTimeField(blank=True, null=True)),
                (
                    "reason",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rpc.blockingreason",
                    ),
                ),
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="rpc.rfctobe"
                    ),
                ),
            ],
            options={
                "ordering": ["-since_when"],
            },
        ),
        migrations.CreateModel(
            name="RfcToBeLabel",
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
                    "label",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="rpc.label"
                    ),
                ),
                (
                    "rfctobe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="rpc.rfctobe"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "RfcToBe labels",
            },
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="labels",
            field=models.ManyToManyField(through="rpc.RfcToBeLabel", to="rpc.label"),
        ),
        migrations.CreateModel(
            name="RpcAuthorComment",
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
                ("comment", models.TextField()),
                ("time", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="rpcauthorcomments_by",
                        to="datatracker.datatrackerperson",
                    ),
                ),
                (
                    "datatracker_person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="datatracker.datatrackerperson",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RpcDocumentComment",
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
                ("comment", models.TextField()),
                ("time", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="datatracker.datatrackerperson",
                    ),
                ),
                (
                    "document",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="datatracker.document",
                    ),
                ),
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rpc.rfctobe",
                    ),
                ),
            ],
            bases=(rules.contrib.models.RulesModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="RpcPerson",
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
                ("hours_per_week", models.PositiveSmallIntegerField(default=40)),
                ("is_active", models.BooleanField(default=True)),
                ("capable_of", models.ManyToManyField(blank=True, to="rpc.capability")),
                (
                    "datatracker_person",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="datatracker.datatrackerperson",
                    ),
                ),
                (
                    "manager",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"can_hold_role__slug": "manager"},
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="managed_people",
                        to="rpc.rpcperson",
                    ),
                ),
                ("can_hold_role", models.ManyToManyField(blank=True, to="rpc.rpcrole")),
            ],
        ),
        migrations.CreateModel(
            name="RpcRelatedDocument",
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
                    "relationship",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rpc.docrelationshipname",
                    ),
                ),
                (
                    "source",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="rpc.rfctobe"
                    ),
                ),
                (
                    "target_document",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="rpcrelateddocument_target_set",
                        to="datatracker.document",
                    ),
                ),
                (
                    "target_rfctobe",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="rpcrelateddocument_target_set",
                        to="rpc.rfctobe",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HistoricalAssignment",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("assigned", "Assigned"),
                            ("in_progress", "In Progress"),
                            ("done", "Done"),
                            ("withdrawn", "Withdrawn"),
                            ("closed_for_hold", "Closed For Hold"),
                        ],
                        default="assigned",
                        max_length=32,
                    ),
                ),
                ("comment", models.TextField(blank=True)),
                ("time_spent", models.DurationField(default=datetime.timedelta(0))),
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
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.rfctobe",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.rpcperson",
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.rpcrole",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical assignment",
                "verbose_name_plural": "historical assignments",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="Assignment",
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
                    "state",
                    models.CharField(
                        choices=[
                            ("assigned", "Assigned"),
                            ("in_progress", "In Progress"),
                            ("done", "Done"),
                            ("withdrawn", "Withdrawn"),
                            ("closed_for_hold", "Closed For Hold"),
                        ],
                        default="assigned",
                        max_length=32,
                    ),
                ),
                ("comment", models.TextField(blank=True)),
                ("time_spent", models.DurationField(default=datetime.timedelta(0))),
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="rpc.rfctobe"
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rpc.rpcperson",
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="rpc.rpcrole"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="submitted_format",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="rpc.sourceformatname"
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="publication_std_level",
            field=models.ForeignKey(
                blank=True,
                help_text="StdLevel at publication (blank until published)",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="rpc.stdlevelname",
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="std_level",
            field=models.ForeignKey(
                help_text="Current StdLevel",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="rpc.stdlevelname",
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="publication_stream",
            field=models.ForeignKey(
                blank=True,
                help_text="Stream at publication (blank until published)",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="rpc.streamname",
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="stream",
            field=models.ForeignKey(
                help_text="Current stream",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="rpc.streamname",
            ),
        ),
        migrations.CreateModel(
            name="SubseriesMember",
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
                ("number", models.PositiveIntegerField()),
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="rpc.rfctobe"
                    ),
                ),
                (
                    "type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rpc.subseriestypename",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HistoricalSubseriesMember",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("number", models.PositiveIntegerField()),
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
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.rfctobe",
                    ),
                ),
                (
                    "type",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.subseriestypename",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical subseries member",
                "verbose_name_plural": "historical subseries members",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="boilerplate",
            field=models.ForeignKey(
                help_text="TLP IPR boilerplate option",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="rpc.tlpboilerplatechoicename",
            ),
        ),
        migrations.AddConstraint(
            model_name="clustermember",
            constraint=models.UniqueConstraint(
                deferrable=django.db.models.constraints.Deferrable["DEFERRED"],
                fields=("cluster", "order"),
                name="clustermember_unique_order_in_cluster",
                violation_error_message="order in cluster must be unique",
            ),
        ),
        migrations.AddConstraint(
            model_name="clustermember",
            constraint=models.UniqueConstraint(
                deferrable=django.db.models.constraints.Deferrable["DEFERRED"],
                fields=("doc",),
                name="clustermember_unique_doc",
                violation_error_message=(
                    "A document may not appear in more than one cluster"
                ),
            ),
        ),
        migrations.AddConstraint(
            model_name="rfcauthor",
            constraint=models.UniqueConstraint(
                fields=("datatracker_person", "rfc_to_be"),
                name="unique_author_per_document",
                violation_error_message=(
                    "the person is already an author of this document"
                ),
            ),
        ),
        migrations.AddConstraint(
            model_name="rfcauthor",
            constraint=models.UniqueConstraint(
                deferrable=django.db.models.constraints.Deferrable["DEFERRED"],
                fields=("rfc_to_be", "order"),
                name="unique_author_order_per_document",
                violation_error_message=(
                    "each author order must be unique per document"
                ),
            ),
        ),
        migrations.AddConstraint(
            model_name="metadatavalidationresults",
            constraint=models.UniqueConstraint(
                fields=("rfc_to_be",),
                name="unique_metadata_validation_per_rfc_to_be",
                violation_error_message=(
                    "There can be only one MetadataValidationResults per rfc_to_be.",
                ),
            ),
        ),
        migrations.AddConstraint(
            model_name="actionholder",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("target_document__isnull", True),
                    ("target_rfctobe__isnull", True),
                    _connector="XOR",
                ),
                name="actionholder_exactly_one_target",
                violation_error_message="exactly one target field must be set",
            ),
        ),
        migrations.AddConstraint(
            model_name="actionholder",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("completed__isnull", True),
                    ("datatracker_person__isnull", False),
                    _connector="OR",
                ),
                name="actionholder_completion_requires_person",
                violation_error_message="completion requires a person",
            ),
        ),
        migrations.AddConstraint(
            model_name="rfctobeblockingreason",
            constraint=models.UniqueConstraint(
                condition=models.Q(("resolved__isnull", True)),
                fields=("rfc_to_be", "reason"),
                name="unique_active_blocking_reason_per_rfc",
                violation_error_message=(
                    "This blocking reason is already active for this RFC"
                ),
            ),
        ),
        migrations.AddConstraint(
            model_name="rpcdocumentcomment",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("document__isnull", True),
                    ("rfc_to_be__isnull", True),
                    _connector="XOR",
                ),
                name="rpcdocumentcomment_exactly_one_target",
                violation_error_message="exactly one of doc or rfc_to_be must be set",
            ),
        ),
        migrations.AddConstraint(
            model_name="rpcrelateddocument",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("target_document__isnull", True),
                    ("target_rfctobe__isnull", True),
                    _connector="XOR",
                ),
                name="rpcrelateddocument_exactly_one_target",
                violation_error_message="exactly one target field must be set",
            ),
        ),
        migrations.AddConstraint(
            model_name="rpcrelateddocument",
            constraint=models.UniqueConstraint(
                condition=models.Q(("target_document__isnull", False)),
                fields=("source", "target_document", "relationship"),
                name="unique_source_targetdoc_relationship",
                violation_error_message=(
                    "A source/target_document/relationship combination must be unique."
                ),
            ),
        ),
        migrations.AddConstraint(
            model_name="rpcrelateddocument",
            constraint=models.UniqueConstraint(
                condition=models.Q(("target_rfctobe__isnull", False)),
                fields=("source", "target_rfctobe", "relationship"),
                name="unique_source_targetrfctobe_relationship",
                violation_error_message=(
                    "A source/target_rfctobe/relationship combination must be unique."
                ),
            ),
        ),
        migrations.AddConstraint(
            model_name="assignment",
            constraint=models.UniqueConstraint(
                condition=models.Q(
                    ("state__in", ["done", "withdrawn", "closed_for_hold"]),
                    _negated=True,
                ),
                fields=("person", "rfc_to_be", "role"),
                name="unique_active_assignment_per_person_rfc_role",
                violation_error_message=(
                    "A person can only have one active assignment per RFC and role"
                ),
            ),
        ),
        migrations.AddConstraint(
            model_name="subseriesmember",
            constraint=models.UniqueConstraint(
                fields=("rfc_to_be", "type", "number"),
                name="unique_subseries_member",
                violation_error_message=(
                    "an RfcToBe can only be in the same subseries once"
                ),
            ),
        ),
        migrations.AddConstraint(
            model_name="rfctobe",
            constraint=models.UniqueConstraint(
                fields=("rfc_number",),
                name="unique_non_null_rfc_number",
                nulls_distinct=True,
            ),
        ),
    ]
