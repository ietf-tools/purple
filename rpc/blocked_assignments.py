import logging
from .models import Assignment, RfcToBe, RpcRole

logger = logging.getLogger(__name__)


def is_blocked(rfc: RfcToBe) -> bool:
    """Return True if instance is blocked and can't move forward."""

    # check for blocking labels
    blocking_label = rfc.labels.filter(
        slug__in=["Stream Hold", "IANA Hold", "Tools Issue"]
    ).exists()

    if blocking_label == True:
        return True

    # blocked if draft
    # 1) is in cluster
    # 2) has first_editor finished
    # 3) but others in cluster not yet finished first_editor
    if rfc.cluster is not None:
        first_editor_incomplete = (
            rfc.incomplete_activities().filter(slug="first_editor").exists()
        )
        if first_editor_incomplete == False:  # first_editor is done on this doc
            cluster_members = list(
                rfc.cluster.clustermember_set.select_related("doc").all()
            )
            docs = [m.doc for m in cluster_members if m.doc is not None]
            rfctobes = RfcToBe.objects.filter(draft__in=docs).exclude(
                disposition__slug="withdrawn"
            )
            for r in rfctobes:
                first_editor_incomplete_cluster = (
                    r.incomplete_activities().filter(slug="first_editor").exists()
                )
                if first_editor_incomplete_cluster == False:
                    return True

    # blocked if any related documents not received
    not_received = rfc.rpcrelateddocument_target_set.filter(
        relationship="not-received"
    ).exists()
    if not_received == True:
        return True

    # blocked if active (=incomplete) action holder
    action_holder_active = rfc.actionholder_set.active().exists()
    if action_holder_active == True:
        return True

    return False


def _has_active_blocked_assignment(rfc: RfcToBe) -> bool:
    """Return True if there is an active 'blocked' assignment for this rfc."""
    blocked_qs = rfc.assignment_set.filter(role__slug="blocked").active()

    return blocked_qs.exists()


def _create_blocked_assignment(rfc: RfcToBe) -> bool:
    """Create a new 'blocked' assignment."""

    try:
        role = RpcRole.objects.get(slug="blocked")

        # create assignment without person
        Assignment.objects.create(rfc_to_be=rfc, role=role)
        return True
    except Exception:
        logger.exception(
            "failed to create blocked assignment for rfc %s", getattr(rfc, "pk", None)
        )
        return None


def _close_latest_blocked_assignment(rfc: RfcToBe) -> bool:
    """Mark the latest active 'blocked' assignment as done."""
    blocked_qs = (
        rfc.assignment_set.filter(role__slug="blocked").active().order_by("-pk")
    )

    if not blocked_qs.exists():
        return False

    a = blocked_qs.first()
    a.state = "done"
    a.save(update_fields=["state"])
    return True


def apply_blocked_assignment_for_rfc(rfc: RfcToBe):
    """Main entry: compute blocked state and apply assignment transitions.

    - If moves not-blocked -> blocked: create new 'blocked' assignment.
    - If moves blocked -> not-blocked: mark latest 'blocked' assignment done.
    """
    # don't block if current active assignment exists
    if rfc.assignment_set.exclude(role__slug="blocked").active().exists():
        return

    blocked_now = is_blocked(rfc)
    blocked_before = _has_active_blocked_assignment(rfc)

    if blocked_now and not blocked_before:
        _create_blocked_assignment(rfc)
    elif not blocked_now and blocked_before:
        _close_latest_blocked_assignment(rfc)
