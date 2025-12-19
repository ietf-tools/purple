# Copyright The IETF Trust 2025, All Rights Reserved

import django.db.models.deletion
import django.utils.timezone
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0028_populate_blockingreasons"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
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
            ],
            options={
                "verbose_name": "historical rfc to be blocking reason",
                "verbose_name_plural": "historical rfc to be blocking reasons",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AlterModelOptions(
            name="rfctobeblockingreason",
            options={"ordering": ["-since_when"]},
        ),
        migrations.AddField(
            model_name="rfctobeblockingreason",
            name="resolved",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="rfctobeblockingreason",
            name="since_when",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddConstraint(
            model_name="rfctobeblockingreason",
            constraint=models.UniqueConstraint(
                condition=models.Q(("resolved__isnull", True)),
                fields=("rfc_to_be", "reason"),
                name="unique_active_blocking_reason_per_rfc",
                violation_error_message="This blocking reason is already active for "
                "this RFC",
            ),
        ),
        migrations.AddField(
            model_name="historicalrfctobeblockingreason",
            name="history_user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="historicalrfctobeblockingreason",
            name="reason",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="rpc.blockingreason",
            ),
        ),
        migrations.AddField(
            model_name="historicalrfctobeblockingreason",
            name="rfc_to_be",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="rpc.rfctobe",
            ),
        ),
    ]
