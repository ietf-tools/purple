# Copyright The IETF Trust 2025, All Rights Reserved

from django.contrib import admin
from .models import (
    DumpInfo,
    RpcPerson,
    RfcToBeLabel,
    RfcToBe,
    DispositionName,
    SourceFormatName,
    StdLevelName,
    TlpBoilerplateChoiceName,
    StreamName,
    DocRelationshipName,
    ClusterMember,
    Cluster,
    UnusableRfcNumber,
    RpcRole,
    Capability,
    Assignment,
    RfcAuthor,
    AdditionalEmail,
    FinalApproval,
    ActionHolder,
    RpcRelatedDocument,
    RpcDocumentComment,
    Label,
    RpcAuthorComment,
    ApprovalLogMessage,
)
from simple_history.admin import SimpleHistoryAdmin

admin.site.register(DumpInfo)


class RpcPersonAdmin(admin.ModelAdmin):
    search_fields = ["datatracker_person__datatracker_id"]
    list_display = ["id", "datatracker_person", "can_hold_role__name"]


admin.site.register(RpcPerson, RpcPersonAdmin)
admin.site.register(RfcToBeLabel)


class RfcToBeAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = ["draft", "draft__rev", "rfc_number"]
    search_fields = ["draft__name", "rfc_number"]


admin.site.register(RfcToBe, RfcToBeAdmin)

admin.site.register(DispositionName)
admin.site.register(SourceFormatName)
admin.site.register(StdLevelName)
admin.site.register(TlpBoilerplateChoiceName)
admin.site.register(StreamName)
admin.site.register(DocRelationshipName)
admin.site.register(ClusterMember)
admin.site.register(Cluster)
admin.site.register(UnusableRfcNumber)


class RpcRoleAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "slug"]


admin.site.register(RpcRole, RpcRoleAdmin)
admin.site.register(Capability)


class AssignmentAdmin(admin.ModelAdmin):
    search_fields = ["person__datatracker_person__datatracker_id"]
    list_display = ["id", "rfc_to_be", "person", "role", "state"]


admin.site.register(Assignment, AssignmentAdmin)


class RfcAuthorAdmin(admin.ModelAdmin):
    search_fields = [
        "datatracker_person__datatracker_id",
        "titlepage_name",
        "rfc_to_be__rfc_number",
    ]
    list_display = ["titlepage_name", "rfc_to_be", "is_editor"]


class ApprovalLogMessageAdmin(admin.ModelAdmin):
    list_display = ["id", "rfc_to_be", "time", "by"]
    raw_id_fields = ["rfc_to_be", "by"]
    search_fields = ["rfc_to_be", "by", "log_message"]


admin.site.register(RfcAuthor, RfcAuthorAdmin)
admin.site.register(AdditionalEmail)
admin.site.register(FinalApproval)
admin.site.register(ActionHolder)
admin.site.register(RpcRelatedDocument)
admin.site.register(RpcDocumentComment)
admin.site.register(Label)
admin.site.register(RpcAuthorComment)
admin.site.register(ApprovalLogMessage, ApprovalLogMessageAdmin)
