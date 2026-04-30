# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0022_add_manual_hold_blocking_reason"),
    ]
    operations = [
        migrations.AddField(
            model_name="rfctobeblockingreason",
            name="comment",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalrfctobeblockingreason",
            name="comment",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
    ]
