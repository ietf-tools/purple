# Copyright The IETF Trust 2026, All Rights Reserved

import django.db.models.deletion
import django.utils.timezone
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0002_initial"),
        ("rpc", "0010_add_rfctobe_rev"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalActionHolder",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("body", models.CharField(blank=True, default="", max_length=64)),
                ("since_when", models.DateTimeField(default=django.utils.timezone.now)),
                ("completed", models.DateTimeField(blank=True, null=True)),
                ("deadline", models.DateTimeField(blank=True, null=True)),
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
                    "datatracker_person",
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
                    "target_document",
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
                    "target_rfctobe",
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
                "verbose_name": "historical action holder",
                "verbose_name_plural": "historical action holders",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalRpcAuthorComment",
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
                    "datatracker_person",
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
            ],
            options={
                "verbose_name": "historical rpc author comment",
                "verbose_name_plural": "historical rpc author comments",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalRpcPerson",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("hours_per_week", models.PositiveSmallIntegerField(default=40)),
                ("is_active", models.BooleanField(default=True)),
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
                    "datatracker_person",
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
                    "manager",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        limit_choices_to={"can_hold_role__slug": "manager"},
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.rpcperson",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical rpc person",
                "verbose_name_plural": "historical rpc persons",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalRpcPerson_can_hold_role",
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
                        to="rpc.historicalrpcperson",
                    ),
                ),
                (
                    "rpcperson",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        db_tablespace="",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.rpcperson",
                    ),
                ),
                (
                    "rpcrole",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        db_tablespace="",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.rpcrole",
                    ),
                ),
            ],
            options={
                "verbose_name": "HistoricalRpcPerson_can_hold_role",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalRpcPerson_capable_of",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("m2m_history_id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "capability",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        db_tablespace="",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.capability",
                    ),
                ),
                (
                    "history",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="rpc.historicalrpcperson",
                    ),
                ),
                (
                    "rpcperson",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        db_tablespace="",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="rpc.rpcperson",
                    ),
                ),
            ],
            options={
                "verbose_name": "HistoricalRpcPerson_capable_of",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
