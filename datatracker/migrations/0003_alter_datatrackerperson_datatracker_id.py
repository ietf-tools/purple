# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="datatrackerperson",
            name="datatracker_id",
            field=models.BigIntegerField(
                help_text="ID of the Person in the datatracker"
            ),
        ),
    ]
