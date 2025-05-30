# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0005_approvallogmessage"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicallabel",
            name="is_complexity",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="label",
            name="is_complexity",
            field=models.BooleanField(default=False),
        ),
    ]
