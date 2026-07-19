# Copyright The IETF Trust 2026, All Rights Reserved
"""Shared fixtures and history-rewriting builders for the rpc.stats tests."""

import datetime

from ..factories import AssignmentFactory, RfcToBeFactory, RpcRoleFactory
from ..models import DocRelationshipName, RpcRelatedDocument

UTC = datetime.UTC
DAY = datetime.timedelta(days=1)


def _dt(year, month, day):
    return datetime.datetime(year, month, day, tzinfo=UTC)


def _make_assignment(rfc, role_slug, transitions, person=None):
    """Create an Assignment and rewrite its history to the given transitions.

    ``transitions`` is a list of ``(datetime, state)`` in chronological order;
    the first is the creation state.
    """
    role = RpcRoleFactory(slug=role_slug)
    # person defaults to None to avoid datatracker plain_name lookups in tests.
    assignment = AssignmentFactory(
        rfc_to_be=rfc, role=role, state=transitions[0][1], person=person
    )
    for _when, state in transitions[1:]:
        assignment.state = state
        assignment.save()
    records = list(assignment.history.all().order_by("history_id"))
    assert len(records) == len(transitions), (len(records), len(transitions))
    for record, (when, _state) in zip(records, transitions, strict=True):
        record.history_date = when
        record.save()
    return assignment


def _backdate_creation(rfc, when):
    """Set the doc's creation (enqueue) history date, which drives bin
    membership in the queue rollup."""
    create_rec = rfc.history.filter(history_type="+").order_by("history_date").first()
    create_rec.history_date = when
    create_rec.save()


def _missing_ref_over(rfc, start, end):
    """Give ``rfc`` a not-received reference active over ``[start, end)``."""
    rel, _ = DocRelationshipName.objects.get_or_create(
        slug="not-received", defaults={"name": "Not Received", "desc": ""}
    )
    rrd = RpcRelatedDocument.objects.create(
        relationship=rel, source=rfc, target_rfctobe=RfcToBeFactory()
    )
    hist = RpcRelatedDocument.history
    add = hist.filter(id=rrd.pk, history_type="+").first()
    add.history_date = start
    add.save()
    rid = rrd.pk
    rrd.delete()
    rm = hist.filter(id=rid, history_type="-").order_by("-history_id").first()
    rm.history_date = end
    rm.save()


def _missing_ref_upgraded(rfc, start, upgraded):
    """not-received reference added at ``start``, upgraded to refqueue at
    ``upgraded`` in place (the 1g-resolution path — no delete row)."""
    nr, _ = DocRelationshipName.objects.get_or_create(
        slug="not-received", defaults={"name": "Not Received", "desc": ""}
    )
    refqueue, _ = DocRelationshipName.objects.get_or_create(
        slug="refqueue", defaults={"name": "Ref Queue", "desc": ""}
    )
    rrd = RpcRelatedDocument.objects.create(
        relationship=nr, source=rfc, target_rfctobe=RfcToBeFactory()
    )
    hist = RpcRelatedDocument.history
    add = hist.filter(id=rrd.pk, history_type="+").first()
    add.history_date = start
    add.save()
    rrd.relationship = refqueue  # resolve in place, as rpc.api does for 1g refs
    rrd.save()
    upd = hist.filter(id=rrd.pk, history_type="~").order_by("-history_id").first()
    upd.history_date = upgraded
    upd.save()


def _apply_label_over(rfc, label, start, end):
    """Give ``rfc`` ``label`` for the interval ``[start, end)`` via history."""
    # The document is created before any label is applied, so backdate the
    # creation record (as is always the case in production).
    create_rec = rfc.history.filter(history_type="+").first()
    if create_rec and create_rec.history_date >= start:
        create_rec.history_date = start - DAY
        create_rec.save()
    rfc.labels.add(label)
    add_rec = rfc.history.order_by("-history_id").first()
    add_rec.history_date = start
    add_rec.save()
    rfc.labels.remove(label)
    rm_rec = rfc.history.order_by("-history_id").first()
    rm_rec.history_date = end
    rm_rec.save()
