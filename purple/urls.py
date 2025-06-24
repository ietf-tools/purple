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

from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, register_converter
from rest_framework import routers
from rpc import views
from rpc import api as rpc_api


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

router = routers.DefaultRouter()
router.register(r"assignments", rpc_api.AssignmentViewSet)
router.register(r"capabilities", rpc_api.CapabilityViewSet)
router.register(r"clusters", rpc_api.ClusterViewSet)
router.register(r"documents", rpc_api.RfcToBeViewSet)
router.register(
    r"documents/(?P<draft_name>[^/.]+)/comments",
    rpc_api.DocumentCommentViewSet,
    basename="documents-comments",
)
router.register(
    r"documents/(?P<draft_name>[^/.]+)/authors",
    rpc_api.RpcAuthorViewSet,
    basename="documents-authors",
)
router.register(
    r"documents/(?P<draft_name>[^/.]+)/references",
    rpc_api.RpcRelatedDocumentViewSet,
    basename="documents-references",
)
router.register(r"labels", rpc_api.LabelViewSet)
router.register(r"queue", rpc_api.QueueViewSet, basename="queue")
router.register(r"rpc_person", rpc_api.RpcPersonViewSet)
router.register(
    r"rpc_person/(?P<person_id>[^/.]+)/assignments",
    rpc_api.RpcPersonAssignmentViewSet,
    basename="rpcperson-assignment",
)
router.register(r"rpc_roles", rpc_api.RpcRoleViewSet)
router.register(r"source_format_names", rpc_api.SourceFormatNameViewSet)
router.register(r"std_level_names", rpc_api.StdLevelNameViewSet)
router.register(r"stream_names", rpc_api.StreamNameViewSet)
router.register(
    r"tlp_boilerplate_choice_names", rpc_api.TlpBoilerplateChoiceNameViewSet
)

urlpatterns = [
    path("health/", lambda _: HttpResponse(status=204)),  # no content
    path("admin/", admin.site.urls),
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("login/", views.index),
    path(
        "api/rpc/search/datatrackerpersons/", rpc_api.DatatrackerPersonSearch.as_view()
    ),
    path("api/rpc/profile/", rpc_api.profile),
    path(
        "api/rpc/profile/<int:rpc_person_id>", rpc_api.profile_as_person
    ),  # for demo only
    path("api/rpc/stats/label/", rpc_api.StatsLabels.as_view()),
    path("api/rpc/submissions/", rpc_api.submissions),
    path("api/rpc/submissions/<int:document_id>/", rpc_api.submission),
    path("api/rpc/submissions/<int:document_id>/import/", rpc_api.import_submission),
    path("api/rpc/version/", rpc_api.version),
    path("api/rpc/", include(router.urls)),
]
