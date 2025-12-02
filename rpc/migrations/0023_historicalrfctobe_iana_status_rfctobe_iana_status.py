# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0022_historicalapprovallogmessage"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalrfctobe",
            name="iana_status",
            field=models.CharField(
                choices=[
                    ("no_actions", "This document has no IANA actions"),
                    ("not_completed", "IANA has not completed actions in draft"),
                    ("completed_in_draft", "IANA has completed actions in draft"),
                    (
                        "changes_required",
                        "Changes to registries are required due to RFC edits",
                    ),
                    ("reconciled", "IANA has reconciled changes between draft and RFC"),
                ],
                default="not_completed",
                help_text="Current status of IANA actions for this document",
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="iana_status",
            field=models.CharField(
                choices=[
                    ("no_actions", "This document has no IANA actions"),
                    ("not_completed", "IANA has not completed actions in draft"),
                    ("completed_in_draft", "IANA has completed actions in draft"),
                    (
                        "changes_required",
                        "Changes to registries are required due to RFC edits",
                    ),
                    ("reconciled", "IANA has reconciled changes between draft and RFC"),
                ],
                default="not_completed",
                help_text="Current status of IANA actions for this document",
                max_length=32,
            ),
        ),
    ]
