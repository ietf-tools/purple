# Copyright The IETF Trust 2025, All Rights Reserved

from django.contrib import admin

from .models import (
    Errata,
    Type,
    Status,
    Log,
    AreaAssignment,
)


class ErrataAdmin(admin.ModelAdmin):
    search_fields = ["rfc_to_be__rfc_number"]
    list_display = [
        "rfc_to_be",
        "verifier_dt_person",
        "status",
        "type",
        "submitter_email",
        "submitted_at",
    ]


admin.site.register(Errata, ErrataAdmin)


class TypeAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "used"]


admin.site.register(Type, TypeAdmin)


class StatusAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "used"]


admin.site.register(Status, StatusAdmin)


class LogAdmin(admin.ModelAdmin):
    list_display = [
        "errata",
        "verifier_dt_person",
        "status",
        "type",
        "editor_dt_person",
        "created_at",
    ]


admin.site.register(Log, LogAdmin)


class AreaAssignmentAdmin(admin.ModelAdmin):
    search_fields = ["rfc_to_be__rfc_number", "area_acronym"]
    list_display = ["rfc_to_be", "area_acronym"]


admin.site.register(AreaAssignment, AreaAssignmentAdmin)
