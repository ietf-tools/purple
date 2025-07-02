# Copyright The IETF Trust 2025, All Rights Reserved

import datetime

import django.db.models.constraints
import django.db.models.deletion
import django.utils.timezone
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("datatracker", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
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
                ("slug", models.CharField(max_length=64)),
                ("is_exception", models.BooleanField(default=False)),
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
            name="HistoricalLabel",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("slug", models.CharField(max_length=64)),
                ("is_exception", models.BooleanField(default=False)),
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
                ("rfc_number", models.PositiveIntegerField(null=True)),
                ("external_deadline", models.DateTimeField(null=True)),
                ("internal_goal", models.DateTimeField(null=True)),
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
                    "intended_std_level",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.stdlevelname",
                    ),
                ),
                (
                    "submitted_std_level",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.stdlevelname",
                    ),
                ),
                (
                    "intended_stream",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.streamname",
                    ),
                ),
                (
                    "submitted_stream",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.streamname",
                    ),
                ),
                (
                    "intended_boilerplate",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        help_text="TLP IPR boilerplate option intended to apply upon "
                        "publication as RFC",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.tlpboilerplatechoicename",
                    ),
                ),
                (
                    "submitted_boilerplate",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        help_text="TLP IPR boilerplate option applicable when document "
                        "entered the queue",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.tlpboilerplatechoicename",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical rfc to be",
                "verbose_name_plural": "historical rfc to bes",
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
                ("rfc_number", models.PositiveIntegerField(null=True)),
                ("external_deadline", models.DateTimeField(null=True)),
                ("internal_goal", models.DateTimeField(null=True)),
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
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="datatracker.document",
                    ),
                ),
            ],
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
                    "datatracker_person",
                    models.ForeignKey(
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
        ),
        migrations.CreateModel(
            name="IanaAction",
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
                ("completed", models.DateTimeField(null=True)),
                (
                    "iana_person",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
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
                ("body", models.CharField(blank=True, default="", max_length=64)),
                ("requested", models.DateTimeField(default=django.utils.timezone.now)),
                ("approved", models.DateTimeField(null=True)),
                (
                    "approver",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="approver_set",
                        to="datatracker.datatrackerperson",
                    ),
                ),
                (
                    "overriding_approver",
                    models.ForeignKey(
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
                ("since_when", models.DateTimeField(default=django.utils.timezone.now)),
                ("completed", models.DateTimeField(null=True)),
                ("deadline", models.DateTimeField(null=True)),
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
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="actionholder_set",
                        to="datatracker.document",
                    ),
                ),
                (
                    "target_rfctobe",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="actionholder_set",
                        to="rpc.rfctobe",
                    ),
                ),
            ],
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
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="datatracker.document",
                    ),
                ),
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rpc.rfctobe",
                    ),
                ),
            ],
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
                ("capable_of", models.ManyToManyField(to="rpc.capability")),
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
                        limit_choices_to={"can_hold_role__slug": "manager"},
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="managed_people",
                        to="rpc.rpcperson",
                    ),
                ),
                ("can_hold_role", models.ManyToManyField(to="rpc.rpcrole")),
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
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="rpcrelateddocument_target_set",
                        to="datatracker.document",
                    ),
                ),
                (
                    "target_rfctobe",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="rpcrelateddocument_target_set",
                        to="rpc.rfctobe",
                    ),
                ),
            ],
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
                            ("assigned", "assigned"),
                            ("in progress", "in progress"),
                            ("done", "done"),
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
                        on_delete=django.db.models.deletion.PROTECT, to="rpc.rpcperson"
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
            name="intended_std_level",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="rpc.stdlevelname",
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="submitted_std_level",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="rpc.stdlevelname",
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="intended_stream",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="rpc.streamname",
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="submitted_stream",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="rpc.streamname",
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="intended_boilerplate",
            field=models.ForeignKey(
                help_text="TLP IPR boilerplate option intended to apply upon "
                "publication as RFC",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="rpc.tlpboilerplatechoicename",
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="submitted_boilerplate",
            field=models.ForeignKey(
                help_text="TLP IPR boilerplate option applicable when document entered "
                "the queue",
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
                violation_error_message="A document may not appear in more than "
                "one cluster",
            ),
        ),
        migrations.AddConstraint(
            model_name="finalapproval",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("approved__isnull", True),
                    ("approver__isnull", False),
                    _connector="OR",
                ),
                name="finalapproval_approval_requires_approver",
                violation_error_message="approval requires an approver",
            ),
        ),
        migrations.AddConstraint(
            model_name="finalapproval",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("overriding_approver__isnull", True),
                    ("approver__isnull", False),
                    _connector="OR",
                ),
                name="finalapproval_approval_override_requires_approver",
                violation_error_message="approval override requires an approver be set",
            ),
        ),
        migrations.AddConstraint(
            model_name="finalapproval",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("body", ""), ("overriding_approver__isnull", True), _connector="OR"
                ),
                name="finalapproval_body_approval_no_override",
                violation_error_message="body approval cant be overridden",
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
            model_name="rpcdocumentcomment",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("document__isnull", True),
                    ("rfc_to_be__isnull", True),
                    _connector="XOR",
                ),
                name="rpcdocumentcomment_exactly_one_target",
                violation_error_message="exactly one of document or rfc_to_be must "
                "be set",
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
    ]
