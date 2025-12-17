# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations


def forward(apps, schema_editor):
    BlockingReason = apps.get_model("rpc", "BlockingReason")

    reasons = [
        ("actionholder_active", "Unresolved Action Holder"),
        ("label_stream_hold", "Stream Hold"),
        ("label_extref_hold", "External Reference Hold"),
        ("label_author_input_required", "Author Input Required"),
        ("label_iana_hold", "IANA Hold"),
        ("ref_not_received", "Reference Not Received"),
        ("ref_not_received_2g", "Reference Not Received (2nd Generation)"),
        ("ref_not_received_3g", "Reference Not Received (3rd Generation)"),
        ("refqueue_first_edit_incomplete", "Reference: First Edit Incomplete"),
        ("refqueue_second_edit_incomplete", "Reference: Second Edit Incomplete"),
        ("refqueue_publish_incomplete", "Reference: Publish Incomplete"),
        ("final_approval_pending", "Final Approval Pending"),
        ("tools_issue", "Tools Issue"),
    ]

    for slug, name in reasons:
        BlockingReason.objects.get_or_create(slug=slug, defaults={"name": name})


def reverse(apps, schema_editor):
    BlockingReason = apps.get_model("rpc", "BlockingReason")

    slugs = [
        "actionholder_active",
        "label_stream_hold",
        "label_extref_hold",
        "label_author_input_required",
        "label_iana_hold",
        "ref_not_received",
        "ref_not_received_2g",
        "ref_not_received_3g",
        "refqueue_first_edit_incomplete",
        "refqueue_second_edit_incomplete",
        "refqueue_publish_incomplete",
        "final_approval_pending",
        "tools_issue",
    ]

    BlockingReason.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0027_blockingreason_rfctobeblockingreason"),
    ]
    operations = [migrations.RunPython(forward, reverse)]
