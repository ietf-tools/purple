# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0012_historicalassignment"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalrfctobe",
            name="published_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="published_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
