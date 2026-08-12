# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0011_historicalactionholder_historicalrpcauthorcomment_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicalrfctobe",
            name="publication_stream",
        ),
        migrations.RemoveField(
            model_name="rfctobe",
            name="publication_stream",
        ),
    ]
