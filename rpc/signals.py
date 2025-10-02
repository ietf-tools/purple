from contextlib import contextmanager
from django.db import transaction
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver

from .models import (
    Assignment,
    ActionHolder,
    RfcToBeLabel,
    RpcRelatedDocument,
    ClusterMember,
    RfcToBe,
)
from .blocked_assignments import apply_blocked_assignment_for_rfc


def defer_apply(rfc: RfcToBe | None):
    if not rfc:
        return
    transaction.on_commit(lambda: apply_blocked_assignment_for_rfc(rfc))


@receiver([post_save, post_delete], sender=Assignment)
def assignment_changed(sender, instance: Assignment, **kwargs):
    if instance.role_id == "blocked":
        return
    defer_apply(getattr(instance, "rfc_to_be", None))


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

    @staticmethod
    def process_in_progress_rfctobes():
        """Process all in_progress RfcToBe instances to apply blocked assignments"""
        for rfc in RfcToBe.objects.filter(disposition_id="in_progress"):
            apply_blocked_assignment_for_rfc(rfc)
