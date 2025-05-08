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
    IanaAction,
    ActionHolder,
    RpcRelatedDocument,
    RpcDocumentComment,
    Label,
    RpcAuthorComment,
)

admin.site.register(DumpInfo)
admin.site.register(RpcPerson)
admin.site.register(RfcToBeLabel)
admin.site.register(RfcToBe)
admin.site.register(DispositionName)
admin.site.register(SourceFormatName)
admin.site.register(StdLevelName)
admin.site.register(TlpBoilerplateChoiceName)
admin.site.register(StreamName)
admin.site.register(DocRelationshipName)
admin.site.register(ClusterMember)
admin.site.register(Cluster)
admin.site.register(UnusableRfcNumber)
admin.site.register(RpcRole)
admin.site.register(Capability)
admin.site.register(Assignment)
admin.site.register(RfcAuthor)
admin.site.register(AdditionalEmail)
admin.site.register(FinalApproval)
admin.site.register(IanaAction)
admin.site.register(ActionHolder)
admin.site.register(RpcRelatedDocument)
admin.site.register(RpcDocumentComment)
admin.site.register(Label)
admin.site.register(RpcAuthorComment)
