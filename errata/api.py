from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, viewsets

from .models import Errata
from .serializers import ErrataSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List errata",
        description="Retrieve a list of all errata entries with filtering and "
        "pagination support.",
    ),
    retrieve=extend_schema(
        summary="Get errata details",
        description="Retrieve detailed information about a specific erratum.",
    ),
    create=extend_schema(
        summary="Create errata",
        description="Create a new erratum.",
    ),
    update=extend_schema(
        summary="Update errata",
        description="Update an existing erratum.",
    ),
    partial_update=extend_schema(
        summary="Partially update errata",
        description="Partially update an existing erratum.",
    ),
    destroy=extend_schema(
        summary="Delete errata",
        description="Delete an erratum.",
    ),
)
class ErrataViewSet(viewsets.ModelViewSet):
    """ViewSet for managing errata entries"""

    queryset = Errata.objects.all()
    serializer_class = ErrataSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["status", "type"]
    search_fields = [
        "section",
        "orig_text",
        "corrected_text",
        "submitter_name",
        "submitter_email",
    ]
    ordering_fields = ["created_at", "status"]
    ordering = ["-created_at"]
