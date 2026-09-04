# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations, models
from django.utils import timezone
from django.utils.text import slugify

CHANGE_REASON = "backfill: move slug to text and re-slug (migration 0016)"

# Tracked Label fields to copy into a HistoricalLabel snapshot.
_SNAPSHOT_FIELDS = (
    "slug",
    "text",
    "description",
    "is_exception",
    "is_complexity",
    "color",
    "used",
    "is_public",
)


def backfill_label_text_and_slug(apps, schema_editor):
    """Move each label's old slug into text and re-slug it to kebab-case.

    The old slug doubled as the string readers saw, so it becomes `text`; the new
    slug is slugify(text). Migrations bypass simple-history's signals, so a snapshot is
    written per row (see 0015) to keep history consistent and avoid the change
    being misattributed to the next in-app editor.
    """
    Label = apps.get_model("rpc", "Label")
    Historical = apps.get_model("rpc", "HistoricalLabel")

    assigned: set[str] = set()
    for label in Label.objects.all():
        label.text = label.slug
        # kebab-case; slugify keeps underscores, so convert those to hyphens too.
        base = slugify(label.slug).replace("_", "-") or f"label-{label.id}"
        candidate = base[:64]
        n = 2
        while candidate in assigned:
            candidate = f"{base[:60]}-{n}"
            n += 1
        assigned.add(candidate)
        label.slug = candidate
        label.save(update_fields=["text", "slug"])
        Historical.objects.create(
            history_date=timezone.now(),
            history_type="~",
            history_change_reason=CHANGE_REASON,
            history_user_id=None,
            id=label.id,
            **{f: getattr(label, f) for f in _SNAPSHOT_FIELDS},
        )


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0015_backfill_refqueue_target_rfctobe"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicallabel",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="historicallabel",
            name="text",
            field=models.CharField(
                default="",
                help_text="What the label reads as where it is shown.",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="label",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="label",
            name="text",
            field=models.CharField(
                default="",
                help_text="What the label reads as where it is shown.",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="historicallabel",
            name="slug",
            field=models.CharField(
                db_index=True,
                help_text="Stable machine key, auto-generated from text; "
                "referenced in code.",
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="label",
            name="slug",
            field=models.CharField(
                help_text="Stable machine key, auto-generated from text; "
                "referenced in code.",
                max_length=64,
                unique=True,
            ),
        ),
        migrations.RunPython(backfill_label_text_and_slug, migrations.RunPython.noop),
    ]
