# Copyright The IETF Trust 2026, All Rights Reserved

import purple.mail
import rpc.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rpc', '0031_mailmessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailmessage',
            name='cc',
            field=rpc.models.AddressListField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='mailmessage',
            name='message_id',
            field=models.CharField(default=purple.mail.make_message_id, max_length=255),
        ),
        migrations.AlterField(
            model_name='mailmessage',
            name='subject',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='mailmessage',
            name='to',
            field=rpc.models.AddressListField(max_length=1000),
        ),
    ]
