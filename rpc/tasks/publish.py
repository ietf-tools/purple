# Copyright The IETF Trust 2026, All Rights Reserved
from celery import shared_task
from celery.utils.log import get_task_logger

from utils.task_utils import RetryTask

from ..lifecycle.publication import (
    PublicationError,
    TemporaryPublicationError,
    publish_rfctobe,
)
from ..models import RfcToBe

logger = get_task_logger(__name__)


class PublishRfcToBeTask(RetryTask):
    pass


@shared_task(
    bind=True,
    base=PublishRfcToBeTask,
    throws=(RfcToBe.DoesNotExist, PublicationError),
    autoretry_for=(TemporaryPublicationError,),
)
def publish_rfctobe_task(self, rfctobe_id, expected_head):
    rfctobe = RfcToBe.objects.get(pk=rfctobe_id)
    publish_rfctobe(rfctobe, expected_head=expected_head)
