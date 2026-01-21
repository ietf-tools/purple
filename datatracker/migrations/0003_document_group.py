# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="group",
            field=models.CharField(
                blank=True, help_text="Group of draft", max_length=40
            ),
        ),
    ]
