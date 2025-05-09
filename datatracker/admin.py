# Copyright The IETF Trust 2025, All Rights Reserved

from django.contrib import admin

from .models import DatatrackerPerson, Document, DocumentLabel


class DatatrackerPersonAdmin(admin.ModelAdmin):
    search_fields = ["datatracker_id"]


admin.site.register(DatatrackerPerson, DatatrackerPersonAdmin)


class DocumentAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "title", "stream"]


admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentLabel)
