# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rpc', '0008_populate_blockingreasons'),
    ]

    operations = [
        migrations.AddField(
            model_name='finalapproval',
            name='comment',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='historicalfinalapproval',
            name='comment',
            field=models.TextField(blank=True),
        ),
    ]
