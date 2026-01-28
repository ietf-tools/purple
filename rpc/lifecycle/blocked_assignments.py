import logging

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound

from ..models import (
    Assignment,
    BlockingReason,
    DocRelationshipName,
    RfcToBe,
    RfcToBeBlockingReason,
    RpcRole,
)

logger = logging.getLogger(__name__)


def _is_active_or_pending_assignment(rfc: RfcToBe, slugs) -> bool:
    # check for active assignments
    active_assignments_qs = rfc.assignment_set.filter(role__slug__in=slugs).active()

    # check for pending assignments
    pending_assignments_qs = rfc.pending_activities().filter(slug__in=slugs)

    if active_assignments_qs.exists() or pending_assignments_qs.exists():
        return True

    return False


def get_block_reasons(rfc: RfcToBe) -> set[str]:
    """Compute whether blocked and collect blocking reasons."""
    reasons: set[str] = set()

    # Gate 1: Blocks formatting / reference checks
    slugs = ["ref_checker", "formatting"]
    if _is_active_or_pending_assignment(rfc, slugs):
        action_holder_active_qs = rfc.actionholder_set.active()
        if action_holder_active_qs.exists():
            reasons.add(BlockingReason.ACTION_HOLDER_ACTIVE)
        stream_hold_qs = rfc.labels.filter(slug="Stream Hold")
        if stream_hold_qs.exists():
            reasons.add(BlockingReason.LABEL_STREAM_HOLD)
        extref_hold_qs = rfc.labels.filter(slug="ExtRef Hold")
        if extref_hold_qs.exists():
            reasons.add(BlockingReason.LABEL_EXTREF_HOLD)
        author_input_qs = rfc.labels.filter(slug="Author Input Required")
        if author_input_qs.exists():
            reasons.add(BlockingReason.LABEL_AUTHOR_INPUT_REQUIRED)
        # any related documents not received (incl. 2g/3g), return only first
        if rfc.rpcrelateddocument_set.filter(
            relationship__slug=DocRelationshipName.NOT_RECEIVED_RELATIONSHIP_SLUGS
        ).exists():
            if rfc.rpcrelateddocument_set.filter(
                relationship__slug=DocRelationshipName.NOT_RECEIVED_RELATIONSHIP_SLUG
            ).exists():
                reasons.add(BlockingReason.REFERENCE_NOT_RECEIVED)
            elif rfc.rpcrelateddocument_set.filter(
                relationship__slug=DocRelationshipName.NOT_RECEIVED_2G_RELATIONSHIP_SLUG
            ).exists():
                reasons.add(BlockingReason.REFERENCE_NOT_RECEIVED_2G)
                return reasons
            elif rfc.rpcrelateddocument_set.filter(
                relationship__slug=DocRelationshipName.NOT_RECEIVED_3G_RELATIONSHIP_SLUG
            ).exists():
                reasons.add(BlockingReason.REFERENCE_NOT_RECEIVED_3G)
        return reasons

    # Gate 2: Blocks first edit
    slugs = ["first_editor"]
    if _is_active_or_pending_assignment(rfc, slugs):
        action_holder_active_qs = rfc.actionholder_set.active()
        if action_holder_active_qs.exists():
            reasons.add(BlockingReason.ACTION_HOLDER_ACTIVE)
        stream_or_author_hold_qs = rfc.labels.filter(
            slug__in=["Stream Hold", "Author Input Required"]
        )
        if stream_or_author_hold_qs.exists():
            # record specific reasons
            if rfc.labels.filter(slug__in=["Stream Hold"]).exists():
                reasons.add(BlockingReason.LABEL_STREAM_HOLD)
            if rfc.labels.filter(slug__in=["Author Input Required"]).exists():
                reasons.add(BlockingReason.LABEL_AUTHOR_INPUT_REQUIRED)
        return reasons

    # Gate 3: Blocks second edit
    slugs = ["second_editor"]
    if _is_active_or_pending_assignment(rfc, slugs):
        action_holder_active_qs = rfc.actionholder_set.active()
        if action_holder_active_qs.exists():
            reasons.add(BlockingReason.ACTION_HOLDER_ACTIVE)
        labels_qs = rfc.labels.filter(slug__in=["Stream Hold", "IANA Hold"])
        if labels_qs.exists():
            if rfc.labels.filter(slug__in=["Stream Hold"]).exists():
                reasons.add(BlockingReason.LABEL_STREAM_HOLD)
            if rfc.labels.filter(slug__in=["IANA Hold"]).exists():
                reasons.add(BlockingReason.LABEL_IANA_HOLD)
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
                    reasons.add(BlockingReason.REFQUEUE_FIRST_EDIT_INCOMPLETE)
        return reasons

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
                    reasons.add(BlockingReason.REFQUEUE_SECOND_EDIT_INCOMPLETE)
        if rfc.labels.filter(slug__in=["Stream Hold"]).exists():
            reasons.add(BlockingReason.LABEL_STREAM_HOLD)
        if rfc.actionholder_set.active().exists():
            reasons.add(BlockingReason.ACTION_HOLDER_ACTIVE)
        return reasons

    # Gate 5: Blocks publishing
    slugs = ["publisher"]
    if _is_active_or_pending_assignment(rfc, slugs):
        if rfc.labels.filter(slug__in=["Stream Hold"]).exists():
            reasons.add(BlockingReason.LABEL_STREAM_HOLD)
        if rfc.labels.filter(slug__in=["IANA Hold"]).exists():
            reasons.add(BlockingReason.LABEL_IANA_HOLD)
        if rfc.labels.filter(slug__in=["Tools Issue"]).exists():
            reasons.add(BlockingReason.TOOLS_ISSUE)
        # any document this draft normatively references has not been published
        refqueue_qs = rfc.rpcrelateddocument_set.filter(relationship="refqueue")
        if refqueue_qs.exists():
            for ref in refqueue_qs:
                incomplete_publish_qs = (
                    ref.target_rfctobe.incomplete_activities().filter(slug="publisher")
                )
                if incomplete_publish_qs.exists():
                    reasons.add(BlockingReason.REFQUEUE_PUBLISH_INCOMPLETE)
        if rfc.finalapproval_set.active().exists():
            reasons.add(BlockingReason.FINAL_APPROVAL_PENDING)
        return reasons

    # No active assignments in any gate - return empty set
    return reasons


def _has_active_blocked_assignment(rfc: RfcToBe) -> bool:
    """Return True if there is an active 'blocked' assignment for this rfc."""

    blocked_qs = rfc.assignment_set.filter(role__slug="blocked").active()

    return blocked_qs.exists()


def _create_blocked_assignments(rfc: RfcToBe, reasons: set[str]) -> bool:
    """Create new 'blocked' assignments and store blocking reasons."""

    logger.info("Creating blocked assignment for rfc %s, reasons: %s", rfc.pk, reasons)

    active_assignment_qs = rfc.assignment_set.exclude(role__slug="blocked").active()
    try:
        role = RpcRole.objects.get(slug="blocked")

        if active_assignment_qs.exists():
            logger.info(
                "Setting active assignments to closed_for_hold for rfc %s", rfc.pk
            )
            for assignment in active_assignment_qs:
                # Close the current assignment
                assignment.state = Assignment.State.CLOSED_FOR_HOLD
                assignment.comment = "Closed due to blocked state"
                assignment.save(update_fields=["state", "comment"])

                comment = (
                    f"blocked because of blocking condition(s): {', '.join(reasons)}; "
                )
                Assignment.objects.update_or_create(
                    rfc_to_be=rfc,
                    role=role,
                    person=assignment.person,
                    state=Assignment.State.IN_PROGRESS,
                    defaults={
                        "comment": comment,
                    },
                )

        # Store blocking reasons in RfcToBeBlockingReason
        for reason_slug in reasons:
            try:
                reason_model = BlockingReason.objects.get(slug=reason_slug)
                RfcToBeBlockingReason.objects.create(
                    rfc_to_be=rfc,
                    reason=reason_model,
                )
            except BlockingReason.DoesNotExist as err:
                logger.exception(
                    "Invalid blocking reason slug '%s' for rfc %s", reason_slug, rfc.pk
                )
                raise NotFound(f"Invalid blocking reason slug: {reason_slug}") from err

    except Exception as err:
        logger.exception(
            "Failed to create blocked assignment for rfc %s", getattr(rfc, "pk", None)
        )
        raise NotFound("Failed to create blocked assignment for rfc") from err

    return True


def _close_blocked_assignments(rfc: RfcToBe) -> bool:
    """Mark active 'blocked' assignments as done and resolve blocking
    reasons. Re-create any assignments closed_for_hold.
    """

    blocked_qs = (
        rfc.assignment_set.filter(role__slug="blocked").active().order_by("-pk")
    )

    if not blocked_qs.exists():
        return False

    for a in blocked_qs:
        a.state = Assignment.State.DONE
        a.save(update_fields=["state"])

        # For each previously blocked assignment, find the corresponding
        # closed_for_hold and create a new assignment with the same person and role
        closed_for_hold_qs = rfc.assignment_set.filter(
            state=Assignment.State.CLOSED_FOR_HOLD,
            person=a.person,
        )
        if closed_for_hold_qs.exists():
            # Find the closed_for_hold assignment with the most recent history_date
            latest_assignment = None
            latest_history_date = None
            for assignment in closed_for_hold_qs:
                hist = assignment.history.order_by("-history_date").first()
                if hist and (
                    latest_history_date is None
                    or hist.history_date > latest_history_date
                ):
                    latest_assignment = assignment
                    latest_history_date = hist.history_date
            if latest_assignment:
                logger.info(
                    "Creating new assignment for last closed_for_hold for "
                    "rfc %s and person %s",
                    rfc.pk,
                    a.person,
                )
                Assignment.objects.update_or_create(
                    rfc_to_be=rfc,
                    role=latest_assignment.role,
                    person=latest_assignment.person,
                    state=Assignment.State.ASSIGNED,
                    defaults={
                        "comment": "Re-created after blocked state cleared",
                    },
                )

    # Resolve all active blocking reasons
    RfcToBeBlockingReason.objects.filter(rfc_to_be=rfc, resolved__isnull=True).update(
        resolved=timezone.now()
    )

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

            block_reasons = get_block_reasons(locked)
            blocked_now = bool(block_reasons)
            blocked_before = _has_active_blocked_assignment(locked)

            logger.info(
                "Applying blocked assignment for rfc %s: "
                "blocked_now=%s, blocked_before=%s, reasons=%s",
                locked.pk,
                blocked_now,
                blocked_before,
                list(block_reasons),
            )

            if blocked_now and not blocked_before:
                _create_blocked_assignments(locked, reasons=block_reasons)
                logger.info("Created blocked assignment for rfc %s", locked.pk)
                return True
            elif not blocked_now and blocked_before:
                logger.info("Closing blocked assignment for rfc %s", locked.pk)
                _close_blocked_assignments(locked)
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
