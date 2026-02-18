# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0010_finalapproval_comment_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="metadatavalidationresults",
            options={
                "ordering": ["-received_at"],
                "verbose_name_plural": "Metadata validation results",
            },
        ),
    ]
