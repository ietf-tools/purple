# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0012_alter_historicalrfctobe_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="actionholder",
            name="body",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
    ]
