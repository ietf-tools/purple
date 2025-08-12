# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0009_alter_actionholder_completed_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicallabel",
            name="used",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="label",
            name="used",
            field=models.BooleanField(default=True),
        ),
    ]
