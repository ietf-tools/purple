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
    transaction.on_commit(lambda rfc=rfc: apply_blocked_assignment_for_rfc(rfc))


@receiver([post_save, post_delete], sender=Assignment)
def assignment_changed(sender, instance, **kwargs):
    if instance.role_id == "blocked":
        return
    defer_apply(getattr(instance, "rfc_to_be", None))


@receiver([post_save, post_delete], sender=ActionHolder)
def actionholder_changed(sender, instance, **kwargs):
    defer_apply(getattr(instance, "rfc_to_be", None))


@receiver([post_save, post_delete], sender=RpcRelatedDocument)
def related_doc_changed(sender, instance, **kwargs):
    defer_apply(getattr(instance, "source", None))
    defer_apply(getattr(instance, "target_rfctobe", None))


@receiver([post_save, post_delete], sender=ClusterMember)
def cluster_member_changed(sender, instance, **kwargs):
    defer_apply(getattr(instance, "rfc_to_be", None))


@receiver(m2m_changed, sender=RfcToBe.labels.through)
def rfc_labels_m2m_changed(sender, instance, action, **kwargs):
    # ignore pre_* actions
    if action.startswith("pre_"):
        return

    defer_apply(instance)
