# Copyright The IETF Trust 2026, All Rights Reserved
"""Backfill of historical RPC assignments, self-contained and schedulable.

Documents published before the move to Purple carry no assignment information
(ietf-tools/purple#1468). The source is the old rfced database's
editor_assignments table, which production has no access to, so the mapping was
resolved offline and is embedded below rather than read from a file -- one file
to review, one file to deploy, nothing to mount or copy into a pod.

Limited to assignments made from 1 January 2026 on: a document is included when
its legacy assignment record was last changed on or after that date. Documents
still in the queue at cutover were transferred with their assignments and are not
repeated here.

Run it from the admin: Periodic Tasks -> add a task named
`rpc.tasks_backfill_assignments.backfill_rfc_assignments`. It defaults to dry_run,
so a mistaken trigger reports and writes nothing; pass {"dry_run": false} to
apply. Once every row is present it is a no-op, so it is safe to leave scheduled.

The audit trail is the HistoricalAssignment rows. Assignments are written with
save() rather than bulk_create -- bulk_create bypasses simple-history's signals
-- and carry CHANGE_REASON, so a backfilled assignment is distinguishable from
one somebody made.

How the legacy record was read. It holds a primary editor, a copy editor, an RFC
editor and a publisher per document, and the RPC settled the reading for this
period rather than per document:
  * primary editor -> first_editor and final_review_editor
  * RFC editor -> second_editor
  * publisher -> publisher
  * Sarah Tarrant did the enqueuing and formatting on every document and Ted
    Harrison the reference check, so those three roles are credited to them
    throughout and the copy editor slot is not read.
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction

from .models import Assignment, RfcToBe, RpcPerson, RpcRole
from .signals import SignalsManager

logger = get_task_logger(__name__)

CHANGE_REASON = "backfill: assignments transferred from the rfced database"
CHUNK = 500

# (datatracker_id, name) -> role slug -> the RFCs that person held that role on.
# The name is for the reader; the lookup uses the datatracker id.
# fmt: off
ASSIGNMENTS: dict[tuple[int, str], dict[str, list[int]]] = {
    (130334, 'Alanna Paloma'): {  # 25 assignment(s)
        "final_review_editor": [9848, 9917, 9922, 9925, 9960, 9961, 9969, 9989, 9990,
            9991],
        "first_editor": [9848, 9917, 9922, 9925, 9960, 9961, 9969, 9989, 9990, 9991],
        "second_editor": [9925, 9928, 9930, 9931, 9944],
    },
    (113811, 'Alice Russo'): {  # 40 assignment(s)
        "final_review_editor": [9910, 9926, 9927, 9929, 9951],
        "first_editor": [9910, 9926, 9927, 9929, 9951],
        "publisher": [8653, 9736, 9743, 9768, 9908, 9924, 9925, 9928, 9945, 9947,
            9950, 9952, 9953, 9963],
        "second_editor": [9849, 9897, 9907, 9910, 9915, 9917, 9926, 9927, 9929, 9940,
            9951, 9956, 9957, 9959, 9962, 9967],
    },
    (114455, 'Jean Mahoney'): {  # 2 assignment(s)
        "final_review_editor": [8653],
        "first_editor": [8653],
    },
    (142097, 'Kaelin Foody'): {  # 20 assignment(s)
        "final_review_editor": [9678, 9743, 9896, 9912, 9913, 9928, 9932, 9944, 9947,
            9959],
        "first_editor": [9678, 9743, 9896, 9912, 9913, 9928, 9932, 9944, 9947, 9959],
    },
    (127686, 'Karen Moore'): {  # 32 assignment(s)
        "final_review_editor": [9897, 9914, 9946, 9949, 9952, 9953, 9967, 9968],
        "first_editor": [9897, 9914, 9946, 9949, 9952, 9953, 9967, 9968],
        "second_editor": [9808, 9908, 9920, 9921, 9922, 9923, 9938, 9939, 9946, 9949,
            9960, 9961, 9969, 9989, 9990, 9991],
    },
    (128311, 'Lynne Bartholomew'): {  # 14 assignment(s)
        "final_review_editor": [9892, 9893, 9894, 9895, 9921, 9923, 9940],
        "first_editor": [9892, 9893, 9894, 9895, 9921, 9923, 9940],
    },
    (134025, 'Madison Church'): {  # 16 assignment(s)
        "final_review_editor": [9849, 9880, 9908, 9930, 9935, 9936, 9962, 9964],
        "first_editor": [9849, 9880, 9908, 9930, 9935, 9936, 9962, 9964],
    },
    (128027, 'Megan Ferguson'): {  # 19 assignment(s)
        "final_review_editor": [9907, 9915, 9956, 9957, 9965, 9972, 9983],
        "first_editor": [9907, 9915, 9956, 9957, 9965, 9972, 9983],
        "second_editor": [9678, 9743, 9965, 9972, 9983],
    },
    (130328, 'Rebecca VanRheenen'): {  # 23 assignment(s)
        "final_review_editor": [9853, 9920, 9948, 9950],
        "first_editor": [9853, 9920, 9948, 9950],
        "second_editor": [9848, 9892, 9893, 9894, 9895, 9896, 9912, 9913, 9914, 9941,
            9945, 9948, 9950, 9952, 9953],
    },
    (104401, 'Sandy Ginoza'): {  # 82 assignment(s)
        "final_review_editor": [9736, 9768, 9924, 9934, 9945, 9963],
        "first_editor": [9736, 9768, 9924, 9934, 9945, 9963],
        "publisher": [9678, 9808, 9848, 9849, 9853, 9880, 9892, 9893, 9894, 9895,
            9896, 9897, 9907, 9910, 9912, 9913, 9914, 9915, 9917, 9920, 9921, 9922,
            9923, 9926, 9927, 9929, 9930, 9931, 9932, 9934, 9935, 9936, 9938, 9939,
            9940, 9944, 9946, 9948, 9949, 9951, 9956, 9957, 9959, 9960, 9961, 9962,
            9964, 9965, 9967, 9968, 9969, 9972, 9983, 9989, 9990, 9991],
        "second_editor": [8653, 9736, 9768, 9853, 9880, 9924, 9932, 9934, 9935, 9936,
            9947, 9963, 9964, 9968],
    },
    (131267, 'Sarah Tarrant'): {  # 152 assignment(s)
        "enqueuer": [8653, 9678, 9736, 9743, 9768, 9808, 9848, 9849, 9853, 9880,
            9892, 9893, 9894, 9895, 9896, 9897, 9907, 9908, 9910, 9912, 9913, 9914,
            9915, 9917, 9920, 9921, 9922, 9923, 9924, 9925, 9926, 9927, 9928, 9929,
            9930, 9931, 9932, 9934, 9935, 9936, 9938, 9939, 9940, 9941, 9944, 9945,
            9946, 9947, 9948, 9949, 9950, 9951, 9952, 9953, 9956, 9957, 9959, 9960,
            9961, 9962, 9963, 9964, 9965, 9967, 9968, 9969, 9972, 9983, 9989, 9990,
            9991],
        "final_review_editor": [9808, 9931, 9938, 9939, 9941],
        "first_editor": [9808, 9931, 9938, 9939, 9941],
        "formatting": [8653, 9678, 9736, 9743, 9768, 9808, 9848, 9849, 9853, 9880,
            9892, 9893, 9894, 9895, 9896, 9897, 9907, 9908, 9910, 9912, 9913, 9914,
            9915, 9917, 9920, 9921, 9922, 9923, 9924, 9925, 9926, 9927, 9928, 9929,
            9930, 9931, 9932, 9934, 9935, 9936, 9938, 9939, 9940, 9941, 9944, 9945,
            9946, 9947, 9948, 9949, 9950, 9951, 9952, 9953, 9956, 9957, 9959, 9960,
            9961, 9962, 9963, 9964, 9965, 9967, 9968, 9969, 9972, 9983, 9989, 9990,
            9991],
    },
    (144033, 'Ted Harrison'): {  # 71 assignment(s)
        "ref_checker": [8653, 9678, 9736, 9743, 9768, 9808, 9848, 9849, 9853, 9880,
            9892, 9893, 9894, 9895, 9896, 9897, 9907, 9908, 9910, 9912, 9913, 9914,
            9915, 9917, 9920, 9921, 9922, 9923, 9924, 9925, 9926, 9927, 9928, 9929,
            9930, 9931, 9932, 9934, 9935, 9936, 9938, 9939, 9940, 9941, 9944, 9945,
            9946, 9947, 9948, 9949, 9950, 9951, 9952, 9953, 9956, 9957, 9959, 9960,
            9961, 9962, 9963, 9964, 9965, 9967, 9968, 9969, 9972, 9983, 9989, 9990,
            9991],
    },
}
# fmt: on


@shared_task(bind=True)
def backfill_rfc_assignments(self, dry_run=True, limit=None):
    """Create the assignments named above that do not exist yet.

    `limit` caps how many are created in one run, counted over the ones still
    missing, so repeated limited runs step through the set.

    Returns a summary dict, which Celery keeps as the task result -- a record of
    what each run did, alongside the per-row history the writes leave behind.
    """
    wanted_rows = [
        (rfc, dt, role)
        for (dt, _name), roles in ASSIGNMENTS.items()
        for role, rfcs in roles.items()
        for rfc in rfcs
    ]

    # Resolve the three lookups in bulk rather than per row.
    rfctobe_id = dict(
        RfcToBe.objects.exclude(rfc_number=None).values_list("rfc_number", "id")
    )
    person_id = dict(
        RpcPerson.objects.values_list("datatracker_person__datatracker_id", "id")
    )
    roles = set(RpcRole.objects.values_list("slug", flat=True))
    # What is already recorded. Keyed without state: a document that already has
    # this person in this role is left alone whatever state it is in, rather than
    # gaining a contradictory second row. The unique constraint would not stop
    # that -- it is partial and excludes `done`.
    existing = set(
        Assignment.objects.values_list("rfc_to_be_id", "person_id", "role_id")
    )

    wanted, unresolved = [], []
    for rfc, dt, role in wanted_rows:
        if rfc not in rfctobe_id:
            unresolved.append(f"RFC {rfc}: no RfcToBe")
        elif dt not in person_id:
            unresolved.append(f"RFC {rfc}: no RpcPerson for datatracker {dt}")
        elif role not in roles:
            unresolved.append(f"RFC {rfc}: no RpcRole {role!r}")
        else:
            key = (rfctobe_id[rfc], person_id[dt], role)
            if key not in existing:
                wanted.append(key)
                existing.add(key)

    already_present = len(wanted_rows) - len(wanted) - len(unresolved)
    if limit:
        wanted = wanted[: int(limit)]

    summary = {
        "rows": len(wanted_rows),
        "already_present": already_present,
        "to_create": len(wanted),
        "unresolved": len(unresolved),
        "unresolved_examples": unresolved[:20],
        "created": 0,
        "dry_run": bool(dry_run),
    }

    if dry_run:
        logger.warning("backfill: DRY RUN, nothing written -- %s", summary)
        return summary

    created = 0
    # Signals off for the duration, as xfer_from_rfced does for the same reason.
    # assignment_changed fires on every Assignment save and defers a blocked-assignment
    # re-evaluation of the document; across ~15k historical rows that is ~15k
    # re-evaluations of documents that were published years ago, and it creates
    # `blocked` assignments as a side effect. Backfilling history should record what
    # happened, not re-run the workflow that reacts to it.
    with SignalsManager.disabled():
        for start in range(0, len(wanted), CHUNK):
            # A transaction per chunk rather than one over the whole run: this
            # table is in use, and one 15k-row transaction holds locks throughout.
            with transaction.atomic():
                for rfc_to_be_id, pid, role in wanted[start : start + CHUNK]:
                    assignment = Assignment(
                        rfc_to_be_id=rfc_to_be_id,
                        person_id=pid,
                        role_id=role,
                        state=Assignment.State.DONE,
                    )
                    assignment._change_reason = CHANGE_REASON
                    assignment.save()
                    created += 1
            logger.info("backfill: %s/%s created", created, len(wanted))

    summary["created"] = created
    logger.info("backfill: finished -- %s", summary)
    return summary
