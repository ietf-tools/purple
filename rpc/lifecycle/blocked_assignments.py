import logging

from django.db import transaction
from rest_framework.exceptions import NotFound

from ..models import Assignment, RfcToBe, RpcRole

logger = logging.getLogger(__name__)


def _is_active_or_pending_assignment(rfc: RfcToBe, slugs) -> bool:
    # check for active assignments
    active_assignments_qs = rfc.assignment_set.filter(role__slug__in=slugs).active()

    # check for pending assignments
    pending_assignments_qs = rfc.pending_activities().filter(slug__in=slugs)

    if active_assignments_qs.exists() or pending_assignments_qs.exists():
        return True

    return False


def is_blocked(rfc: RfcToBe) -> bool:
    """Return True if instance is blocked and can't move forward."""

    # Gate 1: Blocks formatting / reference checks
    slugs = ["ref_checker", "formatting"]
    if _is_active_or_pending_assignment(rfc, slugs):
        action_holder_active_qs = rfc.actionholder_set.active()
        if action_holder_active_qs.exists():
            return True
        blocking_label_qs = rfc.labels.filter(slug__in=["Stream Hold", "ExtRef Hold"])
        if blocking_label_qs.exists():
            return True
        # any related documents not received
        not_received_qs = rfc.rpcrelateddocument_set.filter(relationship="not-received")
        if not_received_qs.exists():
            return True

        return False

    # Gate 2: Blocks first edit
    slugs = ["first_editor"]
    if _is_active_or_pending_assignment(rfc, slugs):
        action_holder_active_qs = rfc.actionholder_set.active()
        if action_holder_active_qs.exists():
            return True
        blocking_label_qs = rfc.labels.filter(slug__in=["Stream Hold"])
        if blocking_label_qs.exists():
            return True

        return False

    # Gate 3: Blocks second edit
    slugs = ["second_editor"]
    if _is_active_or_pending_assignment(rfc, slugs):
        action_holder_active_qs = rfc.actionholder_set.active()
        if action_holder_active_qs.exists():
            return True
        blocking_label_qs = rfc.labels.filter(slug__in=["Stream Hold", "IANA Hold"])
        if blocking_label_qs.exists():
            return True
        # any document this draft normatively references has not completed first edit
        refqueue_qs = rfc.rpcrelateddocument_set.filter(relationship="refqueue")
        if refqueue_qs.exists():
            for ref in refqueue_qs:
                incomplete_first_edit_qs = (
                    ref.target_rfctobe.incomplete_activities().filter(
                        slug="first_editor"
                    )
                )
                if incomplete_first_edit_qs.exists():
                    return True

        return False

    # Gate 4: Blocks final review
    slugs = ["final_review_editor"]
    if _is_active_or_pending_assignment(rfc, slugs):
        # any document this draft normatively references has not completed 2nd edit
        refqueue_qs = rfc.rpcrelateddocument_set.filter(relationship="refqueue")
        if refqueue_qs.exists():
            for ref in refqueue_qs:
                incomplete_second_edit_qs = (
                    ref.target_rfctobe.incomplete_activities().filter(
                        slug="second_editor"
                    )
                )
                if incomplete_second_edit_qs.exists():
                    return True
        blocking_label_qs = rfc.labels.filter(slug__in=["Stream Hold"])
        if blocking_label_qs.exists():
            return True
        action_holder_active_qs = rfc.actionholder_set.active()
        if action_holder_active_qs.exists():
            return True

    # Gate 5: Blocks publishing
    slugs = ["publisher"]
    if _is_active_or_pending_assignment(rfc, slugs):
        blocking_label_qs = rfc.labels.filter(
            slug__in=["Stream Hold", "IANA Hold", "Tools Issue"]
        )
        if blocking_label_qs.exists():
            return True
        # any document this draft normatively references has not been published
        refqueue_qs = rfc.rpcrelateddocument_set.filter(relationship="refqueue")
        if refqueue_qs.exists():
            for ref in refqueue_qs:
                incomplete_publish_qs = (
                    ref.target_rfctobe.incomplete_activities().filter(slug="publisher")
                )
                if incomplete_publish_qs.exists():
                    return True
        final_approval_qs = rfc.finalapproval_set.active()
        if final_approval_qs.exists():
            return True

    return False


def _has_active_blocked_assignment(rfc: RfcToBe) -> bool:
    """Return True if there is an active 'blocked' assignment for this rfc."""

    blocked_qs = rfc.assignment_set.filter(role__slug="blocked").active()

    return blocked_qs.exists()


def _create_blocked_assignment(rfc: RfcToBe) -> bool:
    """Create a new 'blocked' assignment."""

    # if any active non-blocked assignment exists, set status to "closed_for_hold"
    active_assignment_qs = rfc.assignment_set.exclude(role__slug="blocked").active()
    if active_assignment_qs.exists():
        logger.info("Setting active assignments to closed_for_hold for rfc %s", rfc.pk)
        active_assignment_qs.update(state=Assignment.State.CLOSED_FOR_HOLD)

    try:
        role = RpcRole.objects.get(slug="blocked")

        # create assignment without person
        Assignment.objects.create(rfc_to_be=rfc, role=role)
    except Exception as err:
        logger.exception(
            "Failed to create blocked assignment for rfc %s", getattr(rfc, "pk", None)
        )
        raise NotFound("Failed to create blocked assignment for rfc") from err

    return True


def _close_latest_blocked_assignment(rfc: RfcToBe) -> bool:
    """Mark the latest active 'blocked' assignment as done."""

    blocked_qs = (
        rfc.assignment_set.filter(role__slug="blocked").active().order_by("-pk")
    )

    if not blocked_qs.exists():
        return False

    a = blocked_qs.first()
    a.state = Assignment.State.DONE
    a.save(update_fields=["state"])
    return True


def apply_blocked_assignment_for_rfc(rfc: RfcToBe) -> bool:
    """Compute blocked state and apply assignment transitions.

    - If move not-blocked -> blocked: create new 'blocked' assignment.
    - If move blocked -> not-blocked: mark latest 'blocked' assignment done.
    """

    try:
        with transaction.atomic():
            # lock the rfc row to avoid races
            locked = RfcToBe.objects.select_for_update().get(pk=rfc.pk)

            blocked_now = is_blocked(locked)
            blocked_before = _has_active_blocked_assignment(locked)

            logger.info(
                "Applying blocked assignment for rfc %s: "
                "blocked_now=%s, blocked_before=%s",
                locked.pk,
                blocked_now,
                blocked_before,
            )

            if blocked_now and not blocked_before:
                _create_blocked_assignment(locked)
                logger.info("Created blocked assignment for rfc %s", locked.pk)
                return True
            elif not blocked_now and blocked_before:
                logger.info("Closing blocked assignment for rfc %s", locked.pk)
                _close_latest_blocked_assignment(locked)
                return True

            return False
    except Exception as err:
        logger.exception(
            "Failed to apply blocked assignment for rfc %s", getattr(rfc, "pk", None)
        )
        raise RuntimeError("Failed to apply blocked assignment") from err


def update_blocked_assignments_for_in_progress_rfcs():
    """Process all in_progress RfcToBe instances to apply blocked assignments"""
    for rfc in RfcToBe.objects.filter(disposition_id="in_progress"):
        apply_blocked_assignment_for_rfc(rfc)
