# Copyright The IETF Trust 2025, All Rights Reserved
import pydantic
from celery import shared_task

from datatracker.utils.publication import PublicationError, publish_rfc
from rpc.models import RfcToBe
from utils.task_utils import RetryTask


class DatatrackerNotificationTask(RetryTask):
    pass


# todo reconsider retry conditions
# When datatracker is down, gateway error -> PublicationError. That is a condition
# where a retry should be made. Most validation errors, missing RfcToBe, or active
# refusal of publication from datatracker should probably not retry.
@shared_task(
    bind=True,
    base=DatatrackerNotificationTask,
    throws=(RfcToBe.DoesNotExist, PublicationError),
    autoretry_for=(Exception,),
    dont_autoretry_for=(
        RfcToBe.DoesNotExist,
        PublicationError,
        pydantic.ValidationError,
    ),
)
def notify_rfc_published_task(self, rfctobe_id):
    rfctobe = RfcToBe.objects.get(pk=rfctobe_id)
    publish_rfc(rfctobe)
