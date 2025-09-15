# Copyright The IETF Trust 2023, All Rights Reserved

from django.core.management.base import BaseCommand, CommandError, CommandParser

from datatracker.models import DatatrackerPerson, Document

from ...models import (
    ActionHolder,
    Assignment,
    Cluster,
    HistoricalLabel,  # type: ignore (managed by django-simple-history)
    HistoricalRfcToBe,  # type: ignore (managed by django-simple-history)
    HistoricalRfcToBeLabel,  # type: ignore (managed by django-simple-history)
    Label,
    RfcAuthor,
    RfcToBe,
    RpcDocumentComment,
    RpcPerson,
    RpcRelatedDocument,
)


class Command(BaseCommand):
    help = "Remove all data from the database (BE CAREFUL)"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--yes-im-sure", action="store_true", dest="confirm")
        parser.add_argument(
            "--yes-im-surely", action="store_true", dest="user_is_a_wise_guy"
        )

    def handle(self, *args, **options):
        if not options["confirm"]:
            raise CommandError(
                "Must confirm with '--yes-im-sure' on the command line"
                + (
                    b" - and don't call me Shirley \xe2\x9c\x88\xef\xb8\x8f".decode()
                    if options["user_is_a_wise_guy"]
                    else ""
                )
            )

        Assignment.objects.all().delete()
        ActionHolder.objects.all().delete()
        HistoricalRfcToBeLabel.objects.all().delete()
        HistoricalRfcToBe.objects.all().delete()
        HistoricalLabel.objects.all().delete()
        RpcDocumentComment.objects.all().delete()
        RpcRelatedDocument.objects.all().delete()
        RfcAuthor.objects.all().delete()
        RfcToBe.objects.all().delete()
        RpcPerson.objects.all().delete()
        DatatrackerPerson.objects.all().delete()
        Document.objects.all().delete()
        Label.objects.all().delete()
        Cluster.objects.all().delete()
