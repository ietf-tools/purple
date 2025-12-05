# Copyright The IETF Trust 2025, All Rights Reserved

import rpc.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rpc', '0024_historicalcluster_historicalclustermember'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalrfctobe',
            name='iana_status',
            field=models.CharField(blank=True, choices=[('no_actions', 'This document has no IANA actions'), ('not_completed', 'IANA has not completed actions in draft'), ('completed', 'IANA has completed actions in draft'), ('changes_required', 'Changes to registries are required due to RFC edits'), ('reconciled', 'IANA has reconciled changes between draft and RFC')], default='not_completed', help_text='Current status of IANA actions for this document', max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='historicalrfctobe',
            name='rfc_number',
            field=models.PositiveIntegerField(blank=True, db_index=True, null=True, validators=[rpc.models.validate_not_unusable_rfc_number]),
        ),
        migrations.AlterField(
            model_name='rfctobe',
            name='iana_status',
            field=models.CharField(blank=True, choices=[('no_actions', 'This document has no IANA actions'), ('not_completed', 'IANA has not completed actions in draft'), ('completed', 'IANA has completed actions in draft'), ('changes_required', 'Changes to registries are required due to RFC edits'), ('reconciled', 'IANA has reconciled changes between draft and RFC')], default='not_completed', help_text='Current status of IANA actions for this document', max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='rfctobe',
            name='rfc_number',
            field=models.PositiveIntegerField(blank=True, null=True, unique=True, validators=[rpc.models.validate_not_unusable_rfc_number]),
        ),
    ]
