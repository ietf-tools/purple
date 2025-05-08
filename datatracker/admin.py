# Copyright The IETF Trust 2025, All Rights Reserved

from django.contrib import admin

from .models import DatatrackerPerson, Document, DocumentLabel


admin.site.register(DatatrackerPerson)
admin.site.register(Document)
admin.site.register(DocumentLabel)
