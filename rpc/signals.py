from contextlib import contextmanager

from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .lifecycle.blocked_assignments import apply_blocked_assignment_for_rfc
from .models import (
    ActionHolder,
    Assignment,
    ClusterMember,
    FinalApproval,
    RfcToBe,
    RfcToBeLabel,
    RpcPerson,
    RpcRelatedDocument,
)


def defer_apply(rfc: RfcToBe | None):
    if not rfc:
        return
    transaction.on_commit(lambda: apply_blocked_assignment_for_rfc(rfc))


@receiver([post_save, post_delete], sender=Assignment)
def assignment_changed(sender, instance: Assignment, **kwargs):
    if instance.role_id == "blocked":
        return
    rfc = getattr(instance, "rfc_to_be", None)
    defer_apply(rfc)
    # Re-evaluate any RFC that has this rfc as a refqueue target
    if rfc:
        for related in RpcRelatedDocument.objects.filter(
            target_rfctobe=rfc, relationship="refqueue"
        ):
            defer_apply(related.source)


@receiver([post_save, post_delete], sender=ActionHolder)
def actionholder_changed(sender, instance: ActionHolder, **kwargs):
    defer_apply(getattr(instance, "target_rfctobe", None))


@receiver([post_save, post_delete], sender=RpcRelatedDocument)
def related_doc_changed(sender, instance: RpcRelatedDocument, **kwargs):
    defer_apply(getattr(instance, "source", None))


@receiver([post_save, post_delete], sender=ClusterMember)
def cluster_member_changed(sender, instance: ClusterMember, **kwargs):
    rfc_to_be = RfcToBe.objects.filter(draft=instance.doc).first()
    defer_apply(rfc_to_be)


@receiver([post_save, post_delete], sender=FinalApproval)
def final_approval_changed(sender, instance: FinalApproval, **kwargs):
    defer_apply(getattr(instance, "rfc_to_be", None))


@receiver([post_save, post_delete], sender=RpcPerson)
def rpc_person_changed(sender, instance: RpcPerson, **kwargs):
    """Invalidate the person name map cache when RpcPerson records change."""
    from .api import RpcPersonViewSet

    cache.delete(RpcPersonViewSet._NAME_MAP_CACHE_KEY)


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
