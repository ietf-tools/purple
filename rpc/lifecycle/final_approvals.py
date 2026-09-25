"""Ensure each author has a final approver and drop pending ones on removal."""

from rpc.models import FinalApproval, RfcAuthor


def ensure_final_approval_for_author(author: RfcAuthor) -> None:
    """Create a FinalApproval request for an author unless one is already pending.

    Does nothing when the author has no datatracker person.
    """
    if author.datatracker_person_id is None:
        return
    FinalApproval.objects.first_or_create(
        rfc_to_be_id=author.rfc_to_be_id,
        approver_id=author.datatracker_person_id,
        approved=None,
    )


def drop_pending_final_approvals_for_author(author: RfcAuthor) -> None:
    """Withdraw approval requests from an author being removed.

    Only requests still pending are deleted. An approval that was given is kept,
    so removing an author never deletes the record that they approved.
    """
    if author.datatracker_person_id is None:
        return
    FinalApproval.objects.active().filter(
        rfc_to_be_id=author.rfc_to_be_id, approver_id=author.datatracker_person_id
    ).delete()
