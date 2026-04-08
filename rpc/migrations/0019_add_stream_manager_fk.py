# Copyright The IETF Trust 2026, All Rights Reserved

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0003_document_group"),
        ("rpc", "0018_alter_publicationattempt_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalrfctobe",
            name="stream_manager",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Responsible party for this document based on stream",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="datatracker.datatrackerperson",
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="stream_manager",
            field=models.ForeignKey(
                blank=True,
                help_text="Responsible party for this document based on stream",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="datatracker.datatrackerperson",
            ),
        ),
    ]
