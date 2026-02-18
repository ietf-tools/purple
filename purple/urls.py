# Copyright The IETF Trust 2023-2025, All Rights Reserved
"""
URL configuration for rpc project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, register_converter
from rest_framework import routers

from rpc import api as rpc_api
from rpc import views


class DraftNameConverter:
    regex = "draft(-[a-z0-9]+)+"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


class RfcNumberConverter:
    regex = "rfc(1-9)[0-9]+"

    def to_python(self, value):
        return int(value[3:])

    def to_url(self, value):
        return f"rfc{value:d}"


register_converter(DraftNameConverter, "draft-name")
register_converter(RfcNumberConverter, "rfc-number")

rpc_router = routers.DefaultRouter()
rpc_router.register(r"assignments", rpc_api.AssignmentViewSet)
rpc_router.register(r"capabilities", rpc_api.CapabilityViewSet)
rpc_router.register(r"clusters", rpc_api.ClusterViewSet)
rpc_router.register(r"documents", rpc_api.RfcToBeViewSet)
rpc_router.register(
    r"documents/(?P<draft_name>[^/.]+)/comments",
    rpc_api.DocumentCommentViewSet,
    basename="documents-comments",
)
rpc_router.register(
    r"documents/(?P<draft_name>[^/.]+)/authors",
    rpc_api.RpcAuthorViewSet,
    basename="documents-authors",
)
rpc_router.register(
    r"documents/(?P<draft_name>[^/.]+)/references",
    rpc_api.RpcDocumentReferencesViewSet,
    basename="documents-references",
)
rpc_router.register(
    r"documents/(?P<draft_name>[^/.]+)/related",
    rpc_api.RpcRelatedDocumentViewSet,
    basename="documents-related",
)
rpc_router.register(
    r"documents/(?P<draft_name>[^/.]+)/final_approvals",
    rpc_api.FinalApprovalViewSet,
    basename="documents-final-approvals",
)
rpc_router.register(
    r"documents/(?P<draft_name>[^/.]+)/action_holders",
    rpc_api.ActionHolderViewSet,
    basename="documents-action-holders",
)
rpc_router.register(
    r"documents/(?P<draft_name>[^/.]+)/approval_logs",
    rpc_api.ApprovalLogMessageViewSet,
    basename="documents-approval-log-messages",
)
rpc_router.register(
    r"documents/(?P<draft_name>[^/.]+)/additional_emails",
    rpc_api.AdditionalEmailViewSet,
    basename="documents-additional-emails",
)
rpc_router.register(
    r"documents/(?P<draft_name>[^/.]+)/metadata_validation_results",
    rpc_api.MetadataValidationResultsViewSet,
    basename="documents-metadata-validation-results",
)
rpc_router.register(r"labels", rpc_api.LabelViewSet)
rpc_router.register(r"rpc_person", rpc_api.RpcPersonViewSet)
rpc_router.register(
    r"rpc_person/(?P<person_id>[^/.]+)/assignments",
    rpc_api.RpcPersonAssignmentViewSet,
    basename="rpcperson-assignment",
)
rpc_router.register(r"rpc_roles", rpc_api.RpcRoleViewSet)
rpc_router.register(r"doc_relationship_names", rpc_api.DocRelationshipNameViewSet)
rpc_router.register(r"source_format_names", rpc_api.SourceFormatNameViewSet)
rpc_router.register(r"std_level_names", rpc_api.StdLevelNameViewSet)
rpc_router.register(r"stream_names", rpc_api.StreamNameViewSet)
rpc_router.register(
    r"tlp_boilerplate_choice_names", rpc_api.TlpBoilerplateChoiceNameViewSet
)
rpc_router.register(r"unusable_rfc_numbers", rpc_api.UnusableRfcNumberViewSet)
rpc_router.register(r"subseries_members", rpc_api.SubseriesMemberViewSet)
rpc_router.register(r"subseries", rpc_api.SubseriesViewSet, basename="subseries")
rpc_router.register(
    r"subseries_types", rpc_api.SubseriesTypeNameViewSet, basename="subseries-types"
)

pubq_router = routers.DefaultRouter()
pubq_router.register(r"clusters", rpc_api.PublicClusterViewSet)

urlpatterns = [
    path("health/", lambda _: HttpResponse(status=204)),  # no content
    path("admin/", admin.site.urls),
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("login/", views.index),
    path("api/pubq/queue/", rpc_api.PublicQueueList.as_view()),
    path("api/rpc/queue/", rpc_api.QueueList.as_view()),
    path(
        "api/rpc/search/datatrackerpersons/", rpc_api.SearchDatatrackerPersons.as_view()
    ),
    path("api/rpc/profile/", rpc_api.profile),
    path(
        "api/rpc/profile/<int:rpc_person_id>", rpc_api.profile_as_person
    ),  # for demo only
    path("api/rpc/mail", rpc_api.Mail.as_view()),
    path("api/rpc/documents/<str:draft_name>/mail", rpc_api.DocumentMail.as_view()),
    path(
        "api/rpc/mailtemplate/<int:rfctobe_id>/",
        rpc_api.RfcMailTemplatesList.as_view(),
    ),
    path("api/rpc/stats/label/", rpc_api.StatsLabels.as_view()),
    path("api/rpc/submissions/", rpc_api.submissions),
    path("api/rpc/submissions/<int:document_id>/", rpc_api.submission),
    path("api/rpc/submissions/<int:document_id>/import/", rpc_api.import_submission),
    path("api/rpc/version/", rpc_api.version),
    path("api/pubq/", include(pubq_router.urls)),
    path("api/rpc/", include(rpc_router.urls)),
]

# Add debug toolbar URLs for development
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
