# Copyright The IETF Trust 2025, All Rights Reserved
import datetime

from celery import Task, shared_task
from celery.utils.log import get_task_logger
from rpcapi_client import (
    AuthorRequest,
    RfcPubRequest,
)

from datatracker.rpcapi import get_rpcapi_client
from rpc.models import RfcToBe

logger = get_task_logger(__name__)


class DatatrackerNotificationTask(Task):
    max_retries = 4 * 24 * 7  # every 15 minutes for a week
    acks_late = True  # task is idempotent; prefer duplicated to lost attempts

    retry_delay_schedule = [3, 3, 6, 10, 15, 30, 60, 120, 240, 480, 900]

    def _retry_delay(self, n):
        if n < len(self.retry_delay_schedule):
            return self.retry_delay_schedule[n]
        return self.retry_delay_schedule[-1]

    def retry(
        self,
        args=None,
        kwargs=None,
        exc=None,
        throw=True,
        eta=None,
        countdown=None,
        max_retries=None,
        **options,
    ):
        if countdown is None:
            countdown = self._retry_delay(self.request.retries)
        super().retry(args, kwargs, exc, throw, eta, countdown, max_retries, **options)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(
            f"Email admins to report failure: {self.name} "
            f"with args={args} and kwargs={kwargs}"
        )


@shared_task(
    bind=True,
    base=DatatrackerNotificationTask,
    throws=(RfcToBe.DoesNotExist,),
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2},
)
def notify_rfc_published_task(self, rfctobe_id):
    # todo upload files
    # todo add guards
    #  - missing rfc_number
    #  - state of rfctobe
    rfctobe = RfcToBe.objects.get(pk=rfctobe_id)
    rpcapi = get_rpcapi_client()
    rpcapi.notify_rfc_published(
        RfcPubRequest(
            published=datetime.datetime.now(tz=datetime.UTC),  # todo real pub date
            draft_name=rfctobe.draft.name,  # todo non-draft RFCs
            draft_rev=rfctobe.draft.rev,
            rfc_number=rfctobe.rfc_number,
            title=rfctobe.draft.title,
            authors=[
                AuthorRequest(
                    titlepage_name=author.titlepage_name,
                    is_editor=author.is_editor,
                    person=(
                        author.datatracker_person.datatracker_id
                        if author.datatracker_person is not None
                        else None
                    ),
                    email=author.datatracker_person.email,
                    affiliation=author.affiliation or "",
                    country="",  # todo author country?
                )
                for author in rfctobe.authors.all()
            ],
            # group=<not implemented, comes from draft>
            stream=rfctobe.intended_stream.slug,
            # abstract="This is the abstract. It is not yet modeled.",
            # pages=None,  # todo pages
            # words=None,  # todo words
            # formal_languages=<not implemented, comes from draft>
            std_level=rfctobe.intended_std_level.slug,
            # ad=<not implemented, comes from draft>
            # note=<not implemented, comes from draft>
            obsoletes=list(
                rfctobe.obsoletes.exclude(
                    # obsoleting an RFC that has no rfc_number is nonsensical, but
                    # guard just in case
                    rfc_number__isnull=True
                ).values_list("rfc_number", flat=True)
            ),
            updates=list(
                rfctobe.updates.exclude(
                    # updating an RFC that has no rfc_number is nonsensical, but
                    # guard just in case
                    rfc_number__isnull=True
                ).values_list("rfc_number", flat=True)
            ),
            subseries=[
                f"{subseries.type.slug}{subseries.number}"
                for subseries in rfctobe.subseriesmember_set.all()
            ],
        )
    )
