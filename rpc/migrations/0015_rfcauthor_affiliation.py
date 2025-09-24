# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0014_alter_assignment_person"),
    ]

    operations = [
        migrations.AddField(
            model_name="rfcauthor",
            name="affiliation",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
