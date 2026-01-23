# Copyright The IETF Trust 2025, All Rights Reserved
from celery import shared_task

from datatracker.utils.publication import (
    publish_rfc,
)
from rpc.lifecycle.publication import PublicationError, TemporaryPublicationError
from rpc.models import RfcToBe
from utils.task_utils import RetryTask


class DatatrackerNotificationTask(RetryTask):
    pass


@shared_task(
    bind=True,
    base=DatatrackerNotificationTask,
    throws=(RfcToBe.DoesNotExist, PublicationError),
    autoretry_for=(TemporaryPublicationError,),
)
def notify_rfc_published_task(self, rfctobe_id):
    rfctobe = RfcToBe.objects.get(pk=rfctobe_id)
    publish_rfc(rfctobe)
