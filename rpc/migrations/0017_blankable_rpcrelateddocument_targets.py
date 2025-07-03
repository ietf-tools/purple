# Copyright The IETF Trust 2025, All Rights Reserved

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0002_initial"),
        ("rpc", "0016_populate_doc_relationship_names"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="historicalrfctobe",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical rfc to be",
                "verbose_name_plural": "historical RfcToBes",
            },
        ),
        migrations.AlterModelOptions(
            name="rfctobe",
            options={"verbose_name_plural": "RfcToBes"},
        ),
        migrations.AlterField(
            model_name="rpcrelateddocument",
            name="target_document",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="rpcrelateddocument_target_set",
                to="datatracker.document",
            ),
        ),
        migrations.AlterField(
            model_name="rpcrelateddocument",
            name="target_rfctobe",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="rpcrelateddocument_target_set",
                to="rpc.rfctobe",
            ),
        ),
        migrations.AlterConstraint(
            model_name="rpcdocumentcomment",
            name="rpcdocumentcomment_exactly_one_target",
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
    ]
