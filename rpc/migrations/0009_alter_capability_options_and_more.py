# Copyright The IETF Trust 2025, All Rights Reserved

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0002_initial"),
        ("rpc", "0008_alter_historicallabel_slug_alter_label_slug"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="capability",
            options={"verbose_name_plural": "capabilities"},
        ),
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
        migrations.AlterModelOptions(
            name="rfctobelabel",
            options={"verbose_name_plural": "RfcToBe labels"},
        ),
        migrations.AlterField(
            model_name="rpcdocumentcomment",
            name="document",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="datatracker.document",
            ),
        ),
        migrations.AlterField(
            model_name="rpcdocumentcomment",
            name="rfc_to_be",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="rpc.rfctobe",
            ),
        ),
    ]
