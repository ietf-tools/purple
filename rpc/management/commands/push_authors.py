# Copyright The IETF Trust 2026, All Rights Reserved
import rpcapi_client
from django.core.management import CommandError
from django.core.management.base import BaseCommand

from datatracker.rpcapi import with_rpcapi
from ...models import RfcToBe


class Command(BaseCommand):
    help = "Push published RfcToBe author data to datatracker (dev only!)"

    @with_rpcapi
    def handle(self, *args, rpcapi: rpcapi_client.PurpleApi, **options):
        for rfc_to_be in RfcToBe.objects.filter(disposition_id="published"):
            patched = rpcapi_client.PatchedEditableRfcRequest(
                authors=[
                    rpcapi_client.RfcAuthorRequest(
                        titlepage_name=author.titlepage_name,
                        is_editor=author.is_editor,
                        person=(
                            author.datatracker_person.datatracker_id
                            if author.datatracker_person is not None
                            else None
                        ),
                        affiliation=author.affiliation or "",
                    )
                    for author in rfc_to_be.authors.all()
                ],
            )
            try:
                rpcapi.purple_rfc_partial_update(
                    rfc_number=str(rfc_to_be.rfc_number),
                    patched_editable_rfc_request=patched,
                )
            except rpcapi_client.exceptions.ApiException as err:
                self.stderr.write(f"Error on {rfc_to_be}: {err}\n")
                raise CommandError from err
