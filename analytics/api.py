# Copyright The IETF Trust 2026, All Rights Reserved
import rpcapi_client
from django.db.models import OuterRef, Prefetch, Subquery
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.views import SpectacularAPIView
from rest_framework.generics import ListAPIView

from datatracker.rpcapi import with_rpcapi
from rpc.models import (
    Assignment,
    ClusterMember,
    DispositionName,
    Label,
    RfcToBe,
    RpcPerson,
    RpcRole,
    SourceFormatName,
)
from rpc.pagination import DefaultLimitOffsetPagination
from rpc.utils import rpc_person_name_map
from utils.rest_framework.authentication import ApiKeyAuthentication
from utils.rest_framework.permissions import HasApiKey

from .serializers import (
    AnalyticsDispositionSerializer,
    AnalyticsDocumentSerializer,
    AnalyticsLabelSerializer,
    AnalyticsRoleSerializer,
    AnalyticsSourceFormatSerializer,
    AnalyticsStaffSerializer,
)

ANALYTICS_API_KEY_ENDPOINT = "api.analytics"


class AnalyticsAutoSchema(AutoSchema):
    def get_tags(self):
        return ["analytics"]


class AnalyticsApiMixin:
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [HasApiKey]
    api_key_endpoint = ANALYTICS_API_KEY_ENDPOINT
    schema = AnalyticsAutoSchema()


class DocumentList(AnalyticsApiMixin, ListAPIView):
    """All documents, in every disposition, with their labels and assignments"""

    serializer_class = AnalyticsDocumentSerializer
    pagination_class = DefaultLimitOffsetPagination
    queryset = (
        RfcToBe.objects.select_related("draft", "disposition", "submitted_format")
        .annotate(
            cluster_number=Subquery(
                ClusterMember.objects.filter(doc=OuterRef("draft")).values(
                    "cluster__number"
                )[:1]
            )
        )
        .prefetch_related(
            "labels",
            Prefetch(
                "assignment_set",
                queryset=Assignment.objects.select_related(
                    "role", "person__datatracker_person"
                ).order_by("pk"),
            ),
        )
        .order_by("-pk")
    )

    @with_rpcapi
    def get_serializer_context(self, rpcapi: rpcapi_client.PurpleApi):
        return super().get_serializer_context() | {
            "name_map": rpc_person_name_map(rpcapi)
        }


class StaffList(AnalyticsApiMixin, ListAPIView):
    """All RPC staff, current and former"""

    serializer_class = AnalyticsStaffSerializer
    queryset = RpcPerson.objects.select_related("datatracker_person").order_by(
        "datatracker_person__datatracker_id"
    )

    @with_rpcapi
    def get_serializer_context(self, rpcapi: rpcapi_client.PurpleApi):
        return super().get_serializer_context() | {
            "name_map": rpc_person_name_map(rpcapi)
        }


class LabelList(AnalyticsApiMixin, ListAPIView):
    """All labels, including unused and non-public ones"""

    serializer_class = AnalyticsLabelSerializer
    queryset = Label.objects.order_by("slug")


class SourceFormatList(AnalyticsApiMixin, ListAPIView):
    """All source formats"""

    serializer_class = AnalyticsSourceFormatSerializer
    queryset = SourceFormatName.objects.order_by("slug")


class RoleList(AnalyticsApiMixin, ListAPIView):
    """All roles staff can hold on a document"""

    serializer_class = AnalyticsRoleSerializer
    queryset = RpcRole.objects.order_by("slug")


class DispositionList(AnalyticsApiMixin, ListAPIView):
    """All document lifecycle states"""

    serializer_class = AnalyticsDispositionSerializer
    queryset = DispositionName.objects.order_by("slug")


@extend_schema_view(get=extend_schema(exclude=True))
class SchemaView(AnalyticsApiMixin, SpectacularAPIView):
    """OpenAPI schema covering only the analytics API"""

    urlconf = "analytics.urls"
    custom_settings = {
        "TITLE": "Purple analytics",
        "DESCRIPTION": "Read-only view of RPC data for the analytics database",
        "SCHEMA_PATH_PREFIX": "/api/analytics/",
        "PREPROCESSING_HOOKS": [],
    }
