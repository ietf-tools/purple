# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0019_add_stream_manager_fk"),
    ]

    operations = [
        migrations.AlterField(
            model_name="clustermember",
            name="order",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="historicalclustermember",
            name="order",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
