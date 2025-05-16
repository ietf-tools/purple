# Copyright The IETF Trust 2025, All Rights Reserved

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import connection


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

        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE errata_log RESTART IDENTITY CASCADE;")
            cursor.execute("TRUNCATE TABLE errata_errata RESTART IDENTITY CASCADE;")
            cursor.execute(
                "TRUNCATE TABLE errata_areaassignment RESTART IDENTITY CASCADE;"
            )

        self.stdout.write(self.style.SUCCESS("Errata data truncated successfully!"))
