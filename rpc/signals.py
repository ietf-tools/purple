from contextlib import contextmanager

from django.db import transaction
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .lifecycle.blocked_assignments import (
    apply_blocked_assignment_for_rfc,
    reference_loop,
)
from .models import (
    ActionHolder,
    Assignment,
    ClusterMember,
    FinalApproval,
    RfcToBe,
    RfcToBeLabel,
    RpcRelatedDocument,
)


def defer_apply(*rfcs: RfcToBe | None, reference_loops: bool = False):
    """Re-evaluate the given documents after commit.

    If reference_loops is set, documents in a reference loop with any of them
    are re-evaluated too. The documents in a loop are unblocked together, so a
    change to one of them, or to a document the loop references, affects all.
    """
    seen: set[int] = set()
    for rfc in rfcs:
        if not rfc or rfc.pk in seen:
            continue
        seen.add(rfc.pk)
        to_apply = [rfc]
        if reference_loops:
            others = reference_loop(rfc) - seen
            seen |= others
            to_apply += RfcToBe.objects.filter(pk__in=others)
        for doc in to_apply:
            transaction.on_commit(lambda doc=doc: apply_blocked_assignment_for_rfc(doc))


@receiver([post_save, post_delete], sender=Assignment)
def assignment_changed(sender, instance: Assignment, **kwargs):
    if instance.role_id == "blocked":
        return
    rfc = getattr(instance, "rfc_to_be", None)
    if not rfc:
        return
    # Re-evaluate any RFC that has this rfc as a refqueue target
    referrers = [
        related.source
        for related in RpcRelatedDocument.objects.filter(
            target_rfctobe=rfc, relationship="refqueue"
        )
    ]
    defer_apply(rfc, *referrers, reference_loops=True)


@receiver([post_save, post_delete], sender=ActionHolder)
def actionholder_changed(sender, instance: ActionHolder, **kwargs):
    rfc = instance.target_rfctobe
    if rfc is None and instance.target_document is not None:
        rfc = RfcToBe.objects.filter(draft=instance.target_document).first()
    defer_apply(rfc)


@receiver([post_save, post_delete], sender=RpcRelatedDocument)
def related_doc_changed(sender, instance: RpcRelatedDocument, **kwargs):
    # The target too: removing a reference can take it out of a loop.
    defer_apply(
        getattr(instance, "source", None),
        getattr(instance, "target_rfctobe", None),
        reference_loops=True,
    )


@receiver([post_save, post_delete], sender=ClusterMember)
def cluster_member_changed(sender, instance: ClusterMember, **kwargs):
    rfc_to_be = RfcToBe.objects.filter(draft=instance.doc).first()
    defer_apply(rfc_to_be)


@receiver([post_save, post_delete], sender=FinalApproval)
def final_approval_changed(sender, instance: FinalApproval, **kwargs):
    defer_apply(getattr(instance, "rfc_to_be", None))


@receiver(m2m_changed, sender=RfcToBe.labels.through)
def rfc_labels_m2m_changed(sender, instance: RfcToBeLabel, action, **kwargs):
    # ignore pre_* actions
    if action.startswith("pre_"):
        return

    defer_apply(instance)


class SignalsManager:
    _SIGNAL_REGISTRY = [
        (post_save, assignment_changed, Assignment),
        (post_delete, assignment_changed, Assignment),
        (post_save, actionholder_changed, ActionHolder),
        (post_delete, actionholder_changed, ActionHolder),
        (post_save, related_doc_changed, RpcRelatedDocument),
        (post_delete, related_doc_changed, RpcRelatedDocument),
        (post_save, cluster_member_changed, ClusterMember),
        (post_delete, cluster_member_changed, ClusterMember),
        (post_save, final_approval_changed, FinalApproval),
        (post_delete, final_approval_changed, FinalApproval),
        (m2m_changed, rfc_labels_m2m_changed, RfcToBe.labels.through),
    ]

    @staticmethod
    @contextmanager
    def disabled():
        """Context manager to temporarily disable signals"""

        SignalsManager.disable()

        try:
            yield
        finally:
            # Re-enable signals when exiting the 'with' block
            SignalsManager.enable()

    @staticmethod
    def disable():
        """Disconnect all registered signals"""
        for signal, handler, sender in SignalsManager._SIGNAL_REGISTRY:
            signal.disconnect(handler, sender=sender)

    @staticmethod
    def enable():
        """Connect all registered signals"""
        for signal, handler, sender in SignalsManager._SIGNAL_REGISTRY:
            signal.connect(handler, sender=sender)
