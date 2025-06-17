# Copyright The IETF Trust 2023-2025, All Rights Reserved

import datetime

from django.db.models import Q
from django.http import JsonResponse
from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from rest_framework.decorators import (
    action,
    api_view,
)
from rest_framework.response import Response
from rest_framework.exceptions import (
    NotAuthenticated,
    PermissionDenied,
    NotFound,
)
from rest_framework import serializers
from rest_framework import mixins, views, viewsets
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    extend_schema_view,
    OpenApiParameter,
)
import rpcapi_client
from rules.contrib.rest_framework import AutoPermissionViewSetMixin

from datatracker.rpcapi import with_rpcapi
from datatracker.models import Document
from .models import (
    Assignment,
    Capability,
    Cluster,
    Label,
    RfcToBe,
    RpcPerson,
    RpcRole,
    SourceFormatName,
    StdLevelName,
    StreamName,
    TlpBoilerplateChoiceName,
    RpcDocumentComment,
)
from .pagination import DefaultLimitOffsetPagination
from .serializers import (
    AssignmentSerializer,
    CapabilitySerializer,
    ClusterSerializer,
    CreateRfcToBeSerializer,
    LabelSerializer,
    NestedAssignmentSerializer,
    QueueItemSerializer,
    RfcToBeSerializer,
    RpcPersonSerializer,
    RpcRoleSerializer,
    SubmissionListItemSerializer,
    Submission,
    SubmissionSerializer,
    SourceFormatNameSerializer,
    StdLevelNameSerializer,
    StreamNameSerializer,
    TlpBoilerplateChoiceNameSerializer,
    VersionInfoSerializer,
    check_user_has_role,
    DocumentCommentSerializer,
)
from .utils import VersionInfo


@api_view(["GET"])
def version(request):
    """Get application version information"""
    return JsonResponse(VersionInfoSerializer(VersionInfo()).data)


@api_view(["GET"])
def profile(request):
    """Get profile of current user"""
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"authenticated": False})
    dt_person = user.datatracker_person()
    # hasattr() test also handles None case
    rpcperson = dt_person.rpcperson if hasattr(dt_person, "rpcperson") else None
    return JsonResponse(
        {
            "authenticated": True,
            "id": user.pk,
            "name": user.name,
            "avatar": user.avatar,
            "rpcPersonId": rpcperson.id if rpcperson is not None else None,
            "isManager": (
                False
                if rpcperson is None
                else rpcperson.can_hold_role.filter(slug="manager").exists()
            ),
        }
    )


# This is for debugging / demo purposes only!
@extend_schema(operation_id="profile_retrieve_demo_only", responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
def profile_as_person(request, rpc_person_id):
    rpcperson = RpcPerson.objects.filter(pk=rpc_person_id).first()
    if rpcperson is None:
        return Response(status=404)
    return JsonResponse(
        {
            "authenticated": request.user.is_authenticated,
            "id": None,
            "name": rpcperson.datatracker_person.plain_name,
            "avatar": f"https://i.pravatar.cc/150?u={rpcperson.datatracker_person.datatracker_id}",
            "rpcPersonId": rpcperson.id,
            "isManager": (
                False
                if rpcperson is None
                else rpcperson.can_hold_role.filter(slug="manager").exists()
            ),
        }
    )


class RpcPersonViewSet(viewsets.ReadOnlyModelViewSet, viewsets.GenericViewSet):
    serializer_class = RpcPersonSerializer
    queryset = RpcPerson.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ["is_active"]

    @with_rpcapi
    def get_serializer_context(self, rpcapi: rpcapi_client.DefaultApi):
        """Add context to the serializer"""
        # use bulk endpoint to get names
        name_map = rpcapi.get_persons(
            list(
                RpcPerson.objects.values_list(
                    "datatracker_person__datatracker_id", flat=True
                )
            )
        )
        return super().get_serializer_context() | {"name_map": name_map}


class RpcPersonAssignmentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Assignments for a specific RPC Person

    URL router must provide the `person_id` kwarg

    TODO: permissions
    """

    queryset = Assignment.objects.exclude(state="done")
    serializer_class = NestedAssignmentSerializer

    def get_queryset(self):
        user = self.request.user
        req_person_id = self.kwargs["person_id"]

        queryset = (
            super()
            .get_queryset()
            .select_related("rfc_to_be")
            .filter(person_id=req_person_id)
        )

        is_manager = check_user_has_role(user, "manager")
        if user.is_superuser or is_manager:
            return queryset

        # Non-superusers/managers should only see their own assignments
        dt_person = (
            user.datatracker_person() if hasattr(user, "datatracker_person") else None
        )
        if (
            dt_person is None
            or not hasattr(dt_person, "rpcperson")
            or dt_person.rpc_person.id != req_person_id
        ):
            raise PermissionDenied("Unauthorized request")

        return queryset


@extend_schema(
    operation_id="submissions_list", responses=SubmissionListItemSerializer(many=True)
)
@api_view(["GET"])
@with_rpcapi
def submissions(request, *, rpcapi: rpcapi_client.DefaultApi):
    """Return documents in datatracker that have been submitted to the RPC but are not yet in the queue

    [
        {
            "id": 123456,
            "name": "draft-foo-bar",
            "stream": "ietf",
            "submitted" : "2023-09-19"
        }
        ...
    ]

    Fed by doing a server->server API query that returns essentially the union of:
    >> Document.objects.filter(states__type_id="draft-iesg",states__slug__in=["approved","ann"])
    <QuerySet [
        <Document: draft-ietf-bess-pbb-evpn-isid-cmacflush>,
        <Document: draft-ietf-dnssd-update-lease>,
        ...
    ]>
    and
    >> Document.objects.filter(states__type_id__in=["draft-stream-iab","draft-stream-irtf","draft-stream-ise"],states__slug__in=["rfc-edit"])
    <QuerySet [
        <Document: draft-iab-m-ten-workshop>,
        <Document: draft-irtf-cfrg-spake2>,
        ...
    ]>
    and SOMETHING ABOUT THE EDITORIAL STREAM...

    Those queries overreturn - there may be things, particularly not from the IETF stream that are already in the queue.
    This api will filter those out.
    """
    # Get submissions list from Datatracker
    response = rpcapi.submitted_to_rpc()
    submitted = response.submitted_to_rpc
    # Filter out I-Ds that already have an RfcToBe
    already_in_queue = RfcToBe.objects.filter(
        draft__datatracker_id__in=[s.id for s in submitted]
    ).values_list("draft__datatracker_id", flat=True)
    submitted = [s for s in submitted if s.id not in already_in_queue]
    return Response(SubmissionListItemSerializer(submitted, many=True).data)


@extend_schema(operation_id="submissions_retrieve", responses=SubmissionSerializer)
@api_view(["GET"])
@with_rpcapi
def submission(request, document_id, rpcapi: rpcapi_client.DefaultApi):
    # Create a Document to which the RfcToBe can refer. If it already exists, update
    # its values with whatever the datatracker currently says.
    draft = rpcapi.get_draft_by_id(document_id)
    subm = Submission.from_rpcapi_draft(draft)
    return Response(SubmissionSerializer(subm).data)


@extend_schema(
    operation_id="submissions_import",
    request=CreateRfcToBeSerializer,
    responses=RfcToBeSerializer,
)
@api_view(["POST"])
@with_rpcapi
def import_submission(request, document_id, rpcapi: rpcapi_client.DefaultApi):
    """View to import a submission and create an RfcToBe"""
    # fetch and create a draft if needed
    try:
        draft = Document.objects.get(datatracker_id=document_id)
    except Document.DoesNotExist:
        draft_info = rpcapi.get_draft_by_id(document_id)
        if draft_info is None:
            return Response(status=404)
        draft, _ = Document.objects.get_or_create(
            datatracker_id=document_id,
            defaults={
                "name": draft_info.name,
                "rev": draft_info.rev,
                "title": draft_info.title,
                "stream": draft_info.stream,
                "pages": draft_info.pages,
                "intended_std_level": draft_info.intended_std_level,
            },
        )

    # Create the RfcToBe
    serializer = CreateRfcToBeSerializer(data=request.data, context={"draft": draft})
    if serializer.is_valid():
        rfctobe = serializer.save()
        return Response(RfcToBeSerializer(rfctobe).data)
    else:
        return Response(serializer.errors, status=400)


class QueueViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    # This is abusing the List action a bit - the "queue" is singular, so this
    # lists its contents. Normally we'd expect the List action to list queues and
    # the Retrieve action to retrieve a single queue. That does not apply to our
    # concept of a singular queue, so I'm using this because it works.
    queryset = RfcToBe.objects.filter(disposition__slug__in=("created", "in_progress"))
    serializer_class = QueueItemSerializer


class CapabilityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Capability.objects.all()
    serializer_class = CapabilitySerializer


class ClusterViewSet(viewsets.ReadOnlyModelViewSet):
    # todo: handle create/update operations and change to viewsets.ModelViewSet
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer
    lookup_field = "number"


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        user = self.request.user

        base_queryset = super().get_queryset()

        is_manager = check_user_has_role(user, "manager")
        if user.is_superuser or is_manager:
            return base_queryset

        # Non-superusers/managers should only see their own assignments
        # more granular permission to be added later
        dt_person = (
            user.datatracker_person() if hasattr(user, "datatracker_person") else None
        )
        if dt_person is None or not hasattr(dt_person, "rpcperson"):
            raise PermissionDenied("Unauthorized request")

        # Filter assignments for the logged-in RpcPerson
        return base_queryset.filter(person=dt_person.rpcperson)


class RfcToBeViewSet(viewsets.ModelViewSet):
    queryset = RfcToBe.objects.all()
    serializer_class = RfcToBeSerializer
    lookup_field = "draft__name"

    @extend_schema(responses=RfcToBeSerializer(many=True))
    @action(detail=False)
    def in_progress(self, request):
        in_progress = RfcToBe.objects.filter(disposition_id="in_progress")
        serializer = self.get_serializer(in_progress, many=True)
        return Response(serializer.data)


class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer


class RpcRoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RpcRole.objects.all()
    serializer_class = RpcRoleSerializer


class StatsLabels(views.APIView):
    @extend_schema(
        operation_id="stats_labels",
        responses=inline_serializer(
            name="LabelStats",
            fields={
                "label_stats": inline_serializer(
                    name="LabelStat",
                    fields={
                        "document_id": serializers.IntegerField(),
                        "label_id": serializers.IntegerField(),
                        "seconds": serializers.FloatField(),
                    },
                    many=True,
                )
            },
        ),
    )
    def get(self, request):
        results = []
        for rtb in RfcToBe.objects.all():
            for label in Label.objects.all():
                seconds_with_label = sum(
                    [
                        interval.end - interval.start
                        for interval in rtb.time_intervals_with_label(label)
                    ],
                    start=datetime.timedelta(0),
                ).total_seconds()
                if seconds_with_label > 0:
                    results.append(
                        {
                            "document_id": rtb.pk,
                            "label_id": label.pk,
                            "seconds": seconds_with_label,
                        }
                    )
        return Response({"label_stats": results})


class SourceFormatNameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SourceFormatName.objects.all()
    serializer_class = SourceFormatNameSerializer


class StdLevelNameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StdLevelName.objects.all()
    serializer_class = StdLevelNameSerializer


class StreamNameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StreamName.objects.all()
    serializer_class = StreamNameSerializer


class TlpBoilerplateChoiceNameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TlpBoilerplateChoiceName.objects.all()
    serializer_class = TlpBoilerplateChoiceNameSerializer


@extend_schema_view(
    list=extend_schema(
        parameters=[OpenApiParameter("draft_name", OpenApiTypes.STR, "path")]
    ),
    update=extend_schema(
        parameters=[OpenApiParameter("draft_name", OpenApiTypes.STR, "path")]
    ),
    partial_update=extend_schema(
        parameters=[OpenApiParameter("draft_name", OpenApiTypes.STR, "path")]
    ),
    create=extend_schema(
        parameters=[OpenApiParameter("draft_name", OpenApiTypes.STR, "path")]
    ),
)
class DocumentCommentViewSet(
    AutoPermissionViewSetMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet for comments on an RfcToBe or datatracker Document"""

    queryset = RpcDocumentComment.objects.all()
    serializer_class = DocumentCommentSerializer
    pagination_class = DefaultLimitOffsetPagination

    def get_queryset(self):
        """Get queryset consisting of all comments for a given draft-name

        Includes comments both on the RfcToBe and on the draft it came from.
        """
        draft_name = self.kwargs["draft_name"]
        return (
            super()
            .get_queryset()
            .filter(Q(rfc_to_be__draft__name=draft_name) | Q(document__name=draft_name))
            .order_by("-time")
        )

    def perform_create(self, serializer):
        """Create a new instance

        The serializer instances has already been set up with validated input data in
        the POST request. This performs additional checks and fills in implicit data
        that are not part of the request body.
        """
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated
        dt_person = user.datatracker_person()
        if dt_person is None or not hasattr(dt_person, "rpcperson"):
            raise PermissionDenied

        # Get ready to save...
        save_kwargs = {"by": dt_person}

        # First, see if we have an RfcToBe for the draft
        draft_name = self.kwargs["draft_name"]
        rfc_to_be = RfcToBe.objects.filter(draft__name=draft_name).first()
        if rfc_to_be is not None:
            save_kwargs["rfc_to_be"] = rfc_to_be
        else:
            # No RfcToBe exists - see if datatracker knows about the draft
            draft = self._draft_by_name(draft_name)
            if draft is not None:
                save_kwargs["document"] = draft
            else:
                raise NotFound  # neither RfcToBe nor draft existed
        # todo permissions check
        serializer.save(**save_kwargs)

    @staticmethod
    @with_rpcapi
    def _draft_by_name(draft_name, *, rpcapi: rpcapi_client.DefaultApi):
        """Get a datatracker Document for a draft given its name

        n.b., creates a Document object if needed
        """
        drafts = rpcapi.get_drafts_by_names([draft_name])
        draft_info = drafts.get(draft_name, None)
        if draft_info is None:
            return None
        # todo manage updates if the details below change before draft reaches pubreq!
        document, _ = Document.objects.get_or_create(
            datatracker_id=draft_info.id,
            defaults={
                "name": draft_info.name,
                "rev": draft_info.rev,
                "title": draft_info.title,
                "stream": draft_info.stream,
                "pages": draft_info.pages,
                "intended_std_level": draft_info.intended_std_level or "",
            },
        )
        return document
