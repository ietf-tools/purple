# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0008_populate_blockingreasons"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalrfctobe",
            name="consensus",
            field=models.BooleanField(
                default=None,
                help_text="Whether document has consensus (None=unknown)",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="consensus",
            field=models.BooleanField(
                default=None,
                help_text="Whether document has consensus (None=unknown)",
                null=True,
            ),
        ),
    ]
