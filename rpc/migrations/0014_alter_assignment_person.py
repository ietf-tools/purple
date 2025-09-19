# Copyright The IETF Trust 2025, All Rights Reserved

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0013_historicalrfctobe_published_date_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assignment",
            name="person",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="rpc.rpcperson",
            ),
        ),
    ]
