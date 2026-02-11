# Copyright The IETF Trust 2025, All Rights Reserved

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    ActionHolder,
    AdditionalEmail,
    ApprovalLogMessage,
    Assignment,
    Capability,
    Cluster,
    ClusterMember,
    DispositionName,
    DocRelationshipName,
    DumpInfo,
    FinalApproval,
    Label,
    MailMessage,
    MetadataValidationResults,
    RfcAuthor,
    RfcToBe,
    RfcToBeLabel,
    RpcAuthorComment,
    RpcDocumentComment,
    RpcPerson,
    RpcRelatedDocument,
    RpcRole,
    SourceFormatName,
    StdLevelName,
    StreamName,
    SubseriesMember,
    TlpBoilerplateChoiceName,
    UnusableRfcNumber,
)


@admin.register(DumpInfo)
class DumpInfoAdmin(admin.ModelAdmin):
    list_display = ["timestamp"]


@admin.register(RpcPerson)
class RpcPersonAdmin(SimpleHistoryAdmin):
    search_fields = ["datatracker_person__datatracker_id"]
    list_display = ["id", "datatracker_person", "can_hold_role__name"]
    list_display_links = ["id", "datatracker_person"]


@admin.register(RfcToBeLabel)
class RfcToBeLabelAdmin(admin.ModelAdmin):
    pass


@admin.register(RfcToBe)
class RfcToBeAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = ["draft", "draft__rev", "rfc_number", "disposition", "repository"]
    list_filter = [
        "disposition",
        "std_level",
        "publication_std_level",
        "stream",
        "publication_stream",
    ]
    search_fields = ["draft__name", "rfc_number", "title", "group", "keywords"]


@admin.register(DispositionName)
class DispositionNameAdmin(admin.ModelAdmin):
    pass


@admin.register(SourceFormatName)
class SourceFormatNameAdmin(admin.ModelAdmin):
    pass


@admin.register(StdLevelName)
class StdLevelNameAdmin(admin.ModelAdmin):
    pass


@admin.register(TlpBoilerplateChoiceName)
class TlpBoilerplateChoiceNameAdmin(admin.ModelAdmin):
    pass


@admin.register(StreamName)
class StreamNameAdmin(admin.ModelAdmin):
    pass


@admin.register(DocRelationshipName)
class DocRelationshipNameAdmin(admin.ModelAdmin):
    pass


class ClusterMemberInline(admin.TabularInline):
    model = ClusterMember
    autocomplete_fields = ["doc"]
    extra = 0


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_display = ["__str__", "members"]
    search_fields = ["number", "clustermember__doc__name"]
    inlines = [ClusterMemberInline]

    def members(self, cluster: Cluster) -> str:
        return ", ".join(member.doc.name for member in cluster.clustermember_set.all())


@admin.register(RpcRole)
class RpcRoleAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "slug"]


@admin.register(Capability)
class CapabilityAdmin(admin.ModelAdmin):
    pass


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    search_fields = ["person__datatracker_person__datatracker_id"]
    list_display = ["id", "__str__", "rfc_to_be", "person", "role", "state"]
    list_display_links = ["id", "__str__"]
    raw_id_fields = ["rfc_to_be", "person"]


@admin.register(RfcAuthor)
class RfcAuthorAdmin(admin.ModelAdmin):
    search_fields = [
        "datatracker_person__datatracker_id",
        "titlepage_name",
        "rfc_to_be__rfc_number",
    ]
    list_display = ["titlepage_name", "rfc_to_be", "is_editor"]


@admin.register(ApprovalLogMessage)
class ApprovalLogMessageAdmin(admin.ModelAdmin):
    list_display = ["id", "rfc_to_be", "time", "by"]
    raw_id_fields = ["rfc_to_be", "by"]
    search_fields = ["rfc_to_be", "by", "log_message"]


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ["slug", "is_complexity", "is_exception", "color"]
    search_fields = ["slug"]
    list_filter = ["is_complexity", "is_exception", "color"]


@admin.register(UnusableRfcNumber)
class UnusableRfcNumberAdmin(admin.ModelAdmin):
    list_display = ["number", "comment"]
    search_fields = ["number", "comment"]


@admin.register(AdditionalEmail)
class AdditionalEmailAdmin(admin.ModelAdmin):
    pass


@admin.register(FinalApproval)
class FinalApprovalAdmin(admin.ModelAdmin):
    pass


@admin.register(ActionHolder)
class ActionHolderAdmin(admin.ModelAdmin):
    pass


@admin.register(RpcRelatedDocument)
class RpcRelatedDocumentAdmin(admin.ModelAdmin):
    pass


@admin.register(RpcDocumentComment)
class RpcDocumentCommentAdmin(admin.ModelAdmin):
    pass


@admin.register(RpcAuthorComment)
class RpcAuthorCommentAdmin(admin.ModelAdmin):
    pass


@admin.register(SubseriesMember)
class SubseriesMemberAdmin(admin.ModelAdmin):
    search_fields = ["number", "type__slug", "rfc_to_be__rfc_number"]


@admin.register(MailMessage)
class MailMessageAdmin(admin.ModelAdmin):
    list_display = ["subject", "msgtype", "to", "message_id", "attempts", "sent"]
    search_fields = ["to", "cc", "subject", "message_id"]
    list_filter = ["msgtype", "sent"]


@admin.register(MetadataValidationResults)
class MetadataValidationResultsAdmin(admin.ModelAdmin):
    list_display = ["rfc_to_be", "status", "received_at"]
    list_filter = ["status"]
    search_fields = ["rfc_to_be__rfc_number", "rfc_to_be__draft__name"]
