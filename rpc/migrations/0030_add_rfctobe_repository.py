# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0029_historicalrfctobeblockingreason_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalrfctobe",
            name="repository",
            field=models.CharField(
                blank=True,
                help_text="Repository name (e.g., ietf-tools/purple)",
                max_length=1000,
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="repository",
            field=models.CharField(
                blank=True,
                help_text="Repository name (e.g., ietf-tools/purple)",
                max_length=1000,
            ),
        ),
    ]
