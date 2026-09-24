"""Add a final approver when an author is added, and drop pending ones when removed."""

from rpc.models import FinalApproval, RfcAuthor


def add_final_approval_for_author(author: RfcAuthor) -> FinalApproval | None:
    """Request final approval from a newly listed author.

    Returns None without writing when the author has no datatracker person, which
    older documents allow, or when an approval from that person already exists,
    which happens when staff added the approver manually first.
    """
    if author.datatracker_person_id is None:
        return None
    existing = FinalApproval.objects.filter(
        rfc_to_be_id=author.rfc_to_be_id, approver_id=author.datatracker_person_id
    )
    if existing.exists():
        return None
    return FinalApproval.objects.create(
        rfc_to_be_id=author.rfc_to_be_id, approver_id=author.datatracker_person_id
    )


def drop_pending_final_approvals_for_author(author: RfcAuthor) -> int:
    """Withdraw approval requests from an author being removed.

    Only requests still pending are deleted. An approval that was given is kept,
    so removing an author never deletes the record that they approved.
    Returns the number of requests deleted.
    """
    if author.datatracker_person_id is None:
        return 0
    deleted, _ = (
        FinalApproval.objects.active()
        .filter(
            rfc_to_be_id=author.rfc_to_be_id, approver_id=author.datatracker_person_id
        )
        .delete()
    )
    return deleted
