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
router.register(r'assignments', rpc_api.AssignmentViewSet)
router.register(r'documents', rpc_api.RfcToBeViewSet)
router.register(r'labels', rpc_api.LabelViewSet)
router.register(r'queue', rpc_api.QueueViewSet, basename="queue")
router.register(r'rpc_roles', rpc_api.RpcRoleViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("login/", views.index),
    path("api/rpc/clusters/", rpc_api.clusters),
    path("api/rpc/clusters/<int:number>", rpc_api.cluster),
    path("api/rpc/profile/", rpc_api.profile),
    path("api/rpc/profile/<int:rpc_person_id>", rpc_api.profile_as_person),  # for demo only
    path("api/rpc/rpc_person/", rpc_api.rpc_person),
    path("api/rpc/stats/label/", rpc_api.StatsLabels.as_view()),
    path("api/rpc/submissions/", rpc_api.submissions),
    path("api/rpc/submissions/<int:document_id>/", rpc_api.submission),
    path("api/rpc/submissions/<int:document_id>/import/", rpc_api.import_submission),
    path("api/rpc/", include(router.urls)),
]
