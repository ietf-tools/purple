import logging

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound

from ..models import (
    Assignment,
    BlockingReason,
    DispositionName,
    DocRelationshipName,
    Notification,
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
    """Compute whether blocked and collect blocking reasons.

    A document in a terminal disposition is never blocked: blocking says work
    cannot proceed, and there is none left.
    """
    if rfc.disposition_id not in DispositionName.ACTIVE_SLUGS:
        return set()

    reasons: set[str] = set()

    # Gate 0: Always blocks regardless of current assignment
    if rfc.labels.filter(slug="author-input-required").exists():
        reasons.add(BlockingReason.LABEL_AUTHOR_INPUT_REQUIRED)
    if rfc.labels.filter(slug="stream-hold").exists():
        reasons.add(BlockingReason.LABEL_STREAM_HOLD)
    if rfc.labels.filter(slug="tools-issue").exists():
        reasons.add(BlockingReason.TOOLS_ISSUE)
    if rfc.rpcrelateddocument_set.filter(
        relationship__slug=DocRelationshipName.NOT_RECEIVED_RELATIONSHIP_SLUG
    ).exists():
        reasons.add(BlockingReason.REFERENCE_NOT_RECEIVED)
    if reasons:
        return reasons

    # Gate 1: Blocks formatting / reference checks
    slugs = ["ref_checker", "formatting"]
    if _is_active_or_pending_assignment(rfc, slugs):
        if rfc.actionholder_set.active().exists():
            reasons.add(BlockingReason.ACTION_HOLDER_ACTIVE)
        if rfc.labels.filter(slug="extref-hold").exists():
            reasons.add(BlockingReason.LABEL_EXTREF_HOLD)
        # any related documents not received (2g/3g/withdrawn), add only first
        blocking_slugs = [
            DocRelationshipName.NOT_RECEIVED_2G_RELATIONSHIP_SLUG,
            DocRelationshipName.NOT_RECEIVED_3G_RELATIONSHIP_SLUG,
            DocRelationshipName.WITHDRAWNREF_RELATIONSHIP_SLUG,
        ]
        if rfc.rpcrelateddocument_set.filter(
            relationship__slug__in=blocking_slugs
        ).exists():
            if rfc.rpcrelateddocument_set.filter(
                relationship__slug=DocRelationshipName.NOT_RECEIVED_2G_RELATIONSHIP_SLUG
            ).exists():
                reasons.add(BlockingReason.REFERENCE_NOT_RECEIVED_2G)
            elif rfc.rpcrelateddocument_set.filter(
                relationship__slug=DocRelationshipName.NOT_RECEIVED_3G_RELATIONSHIP_SLUG
            ).exists():
                reasons.add(BlockingReason.REFERENCE_NOT_RECEIVED_3G)
            elif rfc.rpcrelateddocument_set.filter(
                relationship__slug=DocRelationshipName.WITHDRAWNREF_RELATIONSHIP_SLUG
            ).exists():
                reasons.add(BlockingReason.REFERENCE_NOT_RECEIVED)
        return reasons

    # Gate 2: Blocks first edit
    slugs = ["first_editor"]
    if _is_active_or_pending_assignment(rfc, slugs):
        if rfc.actionholder_set.active().exists():
            reasons.add(BlockingReason.ACTION_HOLDER_ACTIVE)
        return reasons

    # Gate 3: Blocks second edit
    slugs = ["second_editor"]
    if _is_active_or_pending_assignment(rfc, slugs):
        if rfc.actionholder_set.active().exists():
            reasons.add(BlockingReason.ACTION_HOLDER_ACTIVE)
        if rfc.labels.filter(slug="iana-hold").exists():
            reasons.add(BlockingReason.LABEL_IANA_HOLD)
        # any document this draft normatively references has not completed first edit
        refqueue_qs = rfc.rpcrelateddocument_set.filter(relationship="refqueue")
        if refqueue_qs.exists():
            for ref in refqueue_qs:
                target = ref.target_rfctobe
                if (
                    # Not in the queue, so not published.
                    target is None
                    or target.incomplete_activities()
                    .filter(slug="first_editor")
                    .exists()
                ):
                    reasons.add(BlockingReason.REFQUEUE_FIRST_EDIT_INCOMPLETE)
        return reasons

    # Gate 4: Blocks final review
    slugs = ["final_review_editor"]
    if _is_active_or_pending_assignment(rfc, slugs):
        if rfc.actionholder_set.active().exists():
            reasons.add(BlockingReason.ACTION_HOLDER_ACTIVE)
        if rfc.finalapproval_set.active().exists():
            reasons.add(BlockingReason.FINAL_APPROVAL_PENDING)
        return reasons

    # Gate 5: Blocks publishing
    slugs = ["publisher"]
    if _is_active_or_pending_assignment(rfc, slugs):
        if rfc.labels.filter(slug="iana-hold").exists():
            reasons.add(BlockingReason.LABEL_IANA_HOLD)
        # any document this draft normatively references is not ready for publication
        refqueue_qs = rfc.rpcrelateddocument_set.filter(relationship="refqueue")
        if refqueue_qs.exists():
            for ref in refqueue_qs:
                target = ref.target_rfctobe
                if target is None:
                    # Not in the queue, so not published.
                    reasons.add(BlockingReason.REFQUEUE_PUBLISH_INCOMPLETE)
                    continue
                # block if publisher has no done or active assignment
                publisher_qs = target.assignment_set.filter(role__slug="publisher")
                publisher_done_or_active = (
                    publisher_qs.active()
                    | publisher_qs.filter(state=Assignment.State.DONE)
                ).exists()
                if not publisher_done_or_active:
                    reasons.add(BlockingReason.REFQUEUE_PUBLISH_INCOMPLETE)
        if rfc.finalapproval_set.active().exists():
            reasons.add(BlockingReason.FINAL_APPROVAL_PENDING)
        if rfc.actionholder_set.active().exists():
            reasons.add(BlockingReason.ACTION_HOLDER_ACTIVE)
        return reasons

    # No active assignments in any gate - return empty set
    return reasons


def _has_active_blocked_assignment(rfc: RfcToBe) -> bool:
    """Return True if there is an active 'blocked' assignment for this rfc."""

    blocked_qs = rfc.assignment_set.filter(role__slug="blocked").active()

    return blocked_qs.exists()


def _sync_block_reasons(rfc: RfcToBe, reasons: set[str]) -> bool:
    """Resolve stored reasons that no longer apply and store new ones.

    A manual hold is left alone; only apply_manual_unblock resolves it.
    """
    active = RfcToBeBlockingReason.objects.filter(
        rfc_to_be=rfc, resolved__isnull=True
    ).exclude(reason_id=BlockingReason.MANUAL_HOLD)
    stored = set(active.values_list("reason_id", flat=True))
    stale, new = stored - reasons, reasons - stored
    now = timezone.now()
    for reason in active.filter(reason_id__in=stale):
        reason.resolved = now
        reason.save(update_fields=["resolved"])
    for reason_slug in new:
        RfcToBeBlockingReason.objects.create(
            rfc_to_be=rfc, reason_id=reason_slug, comment=""
        )
    if stale or new:
        logger.info(
            "Block reasons for rfc %s: resolved %s, added %s",
            rfc.pk,
            sorted(stale),
            sorted(new),
        )
    return bool(stale or new)


def _create_blocked_assignments(rfc: RfcToBe, reasons: set[str] | None = None) -> bool:
    """Create new 'blocked' assignments and store blocking reasons."""

    logger.info("Creating blocked assignment for rfc %s, reasons: %s", rfc.pk, reasons)

    active_assignment_qs = rfc.assignment_set.exclude(role__slug="blocked").active()
    try:
        _sync_block_reasons(rfc, reasons or set())

        role = RpcRole.objects.get(slug="blocked")

        if active_assignment_qs.exists():
            logger.info(
                "Setting active assignments to closed_for_hold for rfc %s", rfc.pk
            )
            for assignment in active_assignment_qs:
                assignment.state = Assignment.State.CLOSED_FOR_HOLD
                assignment.comment = "Closed due to blocked state"
                assignment.save(update_fields=["state", "comment"])

                Assignment.objects.update_or_create(
                    rfc_to_be=rfc,
                    role=role,
                    person=assignment.person,
                    state=Assignment.State.IN_PROGRESS,
                )

        else:
            logger.info("Creating new blocked assignment for rfc %s", rfc.pk)
            Assignment.objects.create(
                rfc_to_be=rfc,
                role=role,
                state=Assignment.State.IN_PROGRESS,
            )

    except Exception as err:
        logger.exception(
            "Failed to create blocked assignment for rfc %s", getattr(rfc, "pk", None)
        )
        raise NotFound("Failed to create blocked assignment for rfc") from err

    return True


def held_assignments(rfc: RfcToBe) -> list[Assignment]:
    """Return the closed_for_hold assignments of the current block.

    Older holds are skipped: those followed by a done assignment of the role or
    by a later assignment of the same person to it.
    """
    held = []
    seen = set()  # (role, person) pairs with a later assignment
    done_roles = set()  # roles with a later done assignment
    for assignment in rfc.assignment_set.exclude(role__slug="blocked").order_by("-pk"):
        key = (assignment.role_id, assignment.person_id)
        if (
            assignment.state == Assignment.State.CLOSED_FOR_HOLD
            and key not in seen
            and assignment.role_id not in done_roles
        ):
            held.append(assignment)
        seen.add(key)
        if assignment.state == Assignment.State.DONE:
            done_roles.add(assignment.role_id)
    return held


def _hold_new_assignments(rfc: RfcToBe) -> bool:
    """Put assignments made while blocked on hold next to the existing holds."""
    new = list(rfc.assignment_set.exclude(role__slug="blocked").active())
    for assignment in new:
        assignment.state = Assignment.State.CLOSED_FOR_HOLD
        assignment.comment = "Assigned while blocked"
        assignment.save(update_fields=["state", "comment"])
    if new:
        logger.info("Put assignments made while blocked on hold for rfc %s", rfc.pk)
    return bool(new)


def _sync_blocked_assignments(rfc: RfcToBe) -> bool:
    """Keep one blocked assignment per person holding work.

    A document blocked with nobody holding work keeps one without a person, so
    it stays blocked.
    """
    role = RpcRole.objects.get(slug="blocked")
    holders = {h.person for h in held_assignments(rfc)}
    changed = False
    for person in holders:
        if not rfc.assignment_set.filter(role=role, person=person).active().exists():
            Assignment.objects.create(
                rfc_to_be=rfc,
                role=role,
                person=person,
                state=Assignment.State.IN_PROGRESS,
            )
            changed = True
    for blocked in rfc.assignment_set.filter(role=role).active():
        if blocked.person not in holders and (holders or blocked.person is not None):
            blocked.state = Assignment.State.WITHDRAWN
        elif blocked.state != Assignment.State.IN_PROGRESS:
            blocked.state = Assignment.State.IN_PROGRESS
        else:
            continue
        blocked.save(update_fields=["state"])
        changed = True
    if not rfc.assignment_set.filter(role=role).active().exists():
        Assignment.objects.create(
            rfc_to_be=rfc, role=role, state=Assignment.State.IN_PROGRESS
        )
        changed = True
    return changed


def _close_blocked_assignments(rfc: RfcToBe) -> bool:
    """Mark active 'blocked' assignments as done and resolve blocking
    reasons. Give the held assignments back to their people.
    """

    blocked_qs = rfc.assignment_set.filter(role__slug="blocked").active()

    if not blocked_qs.exists():
        return False

    for a in blocked_qs:
        a.state = Assignment.State.DONE
        a.save(update_fields=["state"])

    for held in held_assignments(rfc):
        logger.info(
            "Re-creating held %s assignment for rfc %s and person %s",
            held.role_id,
            rfc.pk,
            held.person,
        )
        Assignment.objects.update_or_create(
            rfc_to_be=rfc,
            role=held.role,
            person=held.person,
            state=Assignment.State.ASSIGNED,
            defaults={
                "comment": "Re-created after blocked state cleared",
            },
        )

    _sync_block_reasons(rfc, set())

    Notification.emit(
        Notification.EventType.UNBLOCKED,
        f"{rfc.name} was unblocked",
        rfc_to_be=rfc,
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
                has_manual_hold = RfcToBeBlockingReason.objects.filter(
                    rfc_to_be=locked,
                    reason_id=BlockingReason.MANUAL_HOLD,
                    resolved__isnull=True,
                ).exists()
                if has_manual_hold:
                    _hold_new_assignments(locked)
                    _sync_blocked_assignments(locked)
                    _sync_block_reasons(locked, set())
                    logger.info(
                        "Automatic block cleared for rfc %s but manual hold active, "
                        "leaving blocked assignment in place",
                        locked.pk,
                    )
                    return False
                logger.info("Closing blocked assignment for rfc %s", locked.pk)
                _close_blocked_assignments(locked)
                return True
            elif blocked_now and blocked_before:
                held_new = _hold_new_assignments(locked)
                blocked_synced = _sync_blocked_assignments(locked)
                reasons_synced = _sync_block_reasons(locked, block_reasons)
                return held_new or blocked_synced or reasons_synced

            return False
    except Exception as err:
        logger.exception(
            "Failed to apply blocked assignment for rfc %s", getattr(rfc, "pk", None)
        )
        raise RuntimeError("Failed to apply blocked assignment") from err


def apply_manual_block(rfc: RfcToBe, comment: str = "") -> None:
    """Store a manual hold reason and create a blocked assignment if needed.

    If the RFC is not yet blocked: closes active assignments to CLOSED_FOR_HOLD
    and creates a new blocked assignment. If already blocked (e.g. an automatic
    block is active), only the reason record is added — no assignment changes.
    """
    try:
        with transaction.atomic():
            locked = RfcToBe.objects.select_for_update().get(pk=rfc.pk)
            RfcToBeBlockingReason.objects.create(
                rfc_to_be=locked, reason_id=BlockingReason.MANUAL_HOLD, comment=comment
            )
            if _has_active_blocked_assignment(locked):
                logger.info(
                    "RFC %s already blocked; skip assignment creation for manual hold",
                    locked.pk,
                )
                return
            # if not already blocked, create blocked assignment
            # don't pass reasons since the current block reason is being added above
            _create_blocked_assignments(locked)
            logger.info("Created manual-hold blocked assignment for rfc %s", locked.pk)
    except Exception as err:
        logger.exception(
            "Failed to apply manual block for rfc %s", getattr(rfc, "pk", None)
        )
        raise RuntimeError("Failed to apply manual block") from err


def apply_manual_unblock(rfc: RfcToBe) -> None:
    """Resolve the manual hold reason and restore assignments if no other blocks remain.

    Marks the blocked assignment done and re-creates any CLOSED_FOR_HOLD assignments —
    but only if no other blocking reasons remain after the hold is removed.
    """
    try:
        with transaction.atomic():
            locked = RfcToBe.objects.select_for_update().get(pk=rfc.pk)
            now = timezone.now()
            for reason in RfcToBeBlockingReason.objects.filter(
                rfc_to_be=locked,
                reason__slug=BlockingReason.MANUAL_HOLD,
                resolved__isnull=True,
            ):
                reason.resolved = now
                reason.save(update_fields=["resolved"])
            remaining_reasons = get_block_reasons(locked)
            if not remaining_reasons and _has_active_blocked_assignment(locked):
                _close_blocked_assignments(locked)
                logger.info(
                    "Closed manual-hold blocked assignment for rfc %s", locked.pk
                )
            else:
                logger.info(
                    "Manual hold cleared for rfc %s but still blocked (%s), "
                    "leaving assignments unchanged",
                    locked.pk,
                    list(remaining_reasons),
                )
    except Exception as err:
        logger.exception(
            "Failed to apply manual unblock for rfc %s", getattr(rfc, "pk", None)
        )
        raise RuntimeError("Failed to apply manual unblock") from err
