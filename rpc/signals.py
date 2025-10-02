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


def defer_apply(rfc: RfcToBe):
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
        post_save.disconnect(assignment_changed, sender=Assignment)
        post_delete.disconnect(assignment_changed, sender=Assignment)
        post_save.disconnect(actionholder_changed, sender=ActionHolder)
        post_delete.disconnect(actionholder_changed, sender=ActionHolder)
        post_save.disconnect(related_doc_changed, sender=RpcRelatedDocument)
        post_delete.disconnect(related_doc_changed, sender=RpcRelatedDocument)
        post_save.disconnect(cluster_member_changed, sender=ClusterMember)
        post_delete.disconnect(cluster_member_changed, sender=ClusterMember)
        m2m_changed.disconnect(rfc_labels_m2m_changed, sender=RfcToBe.labels.through)


    @staticmethod
    def enable():
        post_save.connect(assignment_changed, sender=Assignment)
        post_delete.connect(assignment_changed, sender=Assignment)
        post_save.connect(actionholder_changed, sender=ActionHolder)
        post_delete.connect(actionholder_changed, sender=ActionHolder)
        post_save.connect(related_doc_changed, sender=RpcRelatedDocument)
        post_delete.connect(related_doc_changed, sender=RpcRelatedDocument)
        post_save.connect(cluster_member_changed, sender=ClusterMember)
        post_delete.connect(cluster_member_changed, sender=ClusterMember)
        m2m_changed.connect(rfc_labels_m2m_changed, sender=RfcToBe.labels.through)

    @staticmethod
    def process_in_progress_rfctobes():
        """Process all in_progress RfcToBe instances to apply blocked assignments"""
        for rfc in RfcToBe.objects.filter(disposition_id="in_progress"):
            apply_blocked_assignment_for_rfc(rfc)
