# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0026_alter_rfctobe_rfc_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalrfctobe",
            name="repository",
            field=models.CharField(
                blank=True, help_text="Repository name (e.g., ietf-tools/purple"
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="repository",
            field=models.CharField(
                blank=True, help_text="Repository name (e.g., ietf-tools/purple"
            ),
        ),
    ]
