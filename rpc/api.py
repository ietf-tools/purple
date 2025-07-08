# Copyright The IETF Trust 2023-2025, All Rights Reserved

import datetime
from dataclasses import dataclass

import rpcapi_client
from django.db import transaction
from django.db.models import Max, Q
from django.http import JsonResponse
from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import mixins, serializers, views, viewsets
from rest_framework.decorators import (
    action,
    api_view,
)
from rest_framework.exceptions import (
    NotAuthenticated,
    NotFound,
    PermissionDenied,
)
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rules.contrib.rest_framework import AutoPermissionViewSetMixin

from datatracker.models import DatatrackerPerson, Document
from datatracker.rpcapi import with_rpcapi

from .models import (
    Assignment,
    Capability,
    Cluster,
    Label,
    RfcAuthor,
    RfcToBe,
    RpcDocumentComment,
    RpcPerson,
    RpcRelatedDocument,
    RpcRole,
    SourceFormatName,
    StdLevelName,
    StreamName,
    TlpBoilerplateChoiceName,
)
from .pagination import DefaultLimitOffsetPagination
from .serializers import (
    AssignmentSerializer,
    AuthorOrderSerializer,
    BaseDatatrackerPersonSerializer,
    CapabilitySerializer,
    ClusterSerializer,
    CreateRfcAuthorSerializer,
    CreateRfcToBeSerializer,
    DocumentCommentSerializer,
    LabelSerializer,
    NestedAssignmentSerializer,
    QueueItemSerializer,
    RfcAuthorSerializer,
    RfcToBeSerializer,
    RpcPersonSerializer,
    RpcRelatedDocumentSerializer,
    RpcRoleSerializer,
    SourceFormatNameSerializer,
    StdLevelNameSerializer,
    StreamNameSerializer,
    Submission,
    SubmissionListItemSerializer,
    SubmissionSerializer,
    TlpBoilerplateChoiceNameSerializer,
    VersionInfoSerializer,
    check_user_has_role,
)
from .utils import VersionInfo, create_rpc_related_document


@extend_schema(operation_id="version", responses=VersionInfoSerializer)
@api_view(["GET"])
def version(request):
    """Get application version information"""
    return JsonResponse(VersionInfoSerializer(VersionInfo()).data)


@extend_schema(
    operation_id="profile",
    responses=inline_serializer(
        name="Profile",
        fields={
            "authenticated": serializers.BooleanField(),
            "id": serializers.IntegerField(),
            "name": serializers.CharField(),
            "avatar": serializers.CharField(),
            "rpcPersonId": serializers.IntegerField(allow_null=True),
            "isManager": serializers.BooleanField(),
        },
    ),
)
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


def extend_schema_with_draft_name(actions=None):
    if actions is None:
        actions = [
            "list",
            "retrieve",
            "create",
            "update",
            "partial_update",
            "destroy",
        ]
    return extend_schema_view(
        **{
            action: extend_schema(
                parameters=[OpenApiParameter("draft_name", OpenApiTypes.STR, "path")]
            )
            for action in actions
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
    """Return documents in datatracker that have been submitted to the RPC but are
        not yet in the queue

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
    >>> Document.objects.filter(states__type_id="draft-iesg",
    ... states__slug__in=["approved","ann"])
    <QuerySet [
        <Document: draft-ietf-bess-pbb-evpn-isid-cmacflush>,
        <Document: draft-ietf-dnssd-update-lease>,
        ...
    ]>
    and
    >>> Document.objects.filter(states__type_id__in=["draft-stream-iab",
    ... "draft-stream-irtf","draft-stream-ise"],states__slug__in=["rfc-edit"])
    <QuerySet [
        <Document: draft-iab-m-ten-workshop>,
        <Document: draft-irtf-cfrg-spake2>,
        ...
    ]>
    and SOMETHING ABOUT THE EDITORIAL STREAM...

    Those queries overreturn - there may be things, particularly not from the IETF
    stream that are already in the queue.
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
    serializer = CreateRfcToBeSerializer(data=request.data | {"draft": draft.pk})
    if serializer.is_valid():
        with transaction.atomic():
            rfctobe = serializer.save()

            # Find normative references and store them as RelatedDocs
            # Get ref list from Datatracker
            response = rpcapi.get_draft_references(document_id)
            references = response.references
            # Filter out I-Ds that already have an RfcToBe
            already_in_queue = dict(
                RfcToBe.objects.filter(
                    draft__datatracker_id__in=[s.id for s in references],
                    disposition__slug__in=("created", "in_progress"),
                ).values_list("draft__datatracker_id", "pk")
            )
            rfc_to_be_exists = RfcToBe.objects.filter(
                draft__datatracker_id__in=[s.id for s in references],
            ).values_list("draft__datatracker_id", flat=True)
            for reference in references:
                # Create a RelatedDoc for each normative reference
                if reference.id not in rfc_to_be_exists:
                    # Get the draft for the reference, otherwise create it
                    try:
                        draft = Document.objects.get(datatracker_id=reference.id)
                    except Document.DoesNotExist as err:
                        draft_info = rpcapi.get_draft_by_id(reference.id)
                        if draft_info is None:
                            raise NotFound(
                                "Unable to get draft info for reference"
                            ) from err
                        draft, _ = Document.objects.get_or_create(
                            datatracker_id=reference.id,
                            defaults={
                                "name": draft_info.name,
                                "rev": draft_info.rev,
                                "title": draft_info.title,
                                "stream": draft_info.stream,
                                "pages": draft_info.pages,
                                "intended_std_level": draft_info.intended_std_level,
                            },
                        )
                    create_rpc_related_document("missref", rfctobe.pk, draft.pk)

                if reference.id in already_in_queue:
                    create_rpc_related_document(
                        "refqueue",
                        rfctobe.pk,
                        already_in_queue[reference.id],
                        "rfctobe",
                    )

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


@extend_schema_with_draft_name()
class RpcAuthorViewSet(viewsets.ModelViewSet):
    queryset = RfcAuthor.objects.all()

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(rfc_to_be__draft__name=self.kwargs["draft_name"])
        )

    def perform_create(self, serializer):
        rfc_to_be = RfcToBe.objects.filter(
            draft__name=self.kwargs["draft_name"]
        ).first()
        if rfc_to_be is None:
            raise NotFound("RfcToBe with the given draft name does not exist")
        # Find the current highest order for this document
        max_order = (
            RfcAuthor.objects.filter(rfc_to_be=rfc_to_be)
            .aggregate(max_order=Max("order", default=0))
            .get("max_order")
        )
        serializer.save(rfc_to_be=rfc_to_be, order=max_order + 1)

    def get_serializer_class(self):
        if self.action in ("create"):
            return CreateRfcAuthorSerializer
        return RfcAuthorSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter("draft_name", OpenApiTypes.STR, OpenApiParameter.PATH)
        ],
        responses=AuthorOrderSerializer,
        operation_id="documents_authors_order",
    )
    @action(detail=False, methods=["post"], url_path="order")
    def set_order(self, request, draft_name=None):
        serializer = AuthorOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_list = serializer.validated_data["order"]

        authors = list(RfcAuthor.objects.filter(rfc_to_be__draft__name=draft_name))
        # check that the authors passed in list are identical to the ones currently set
        if len(order_list) != len(authors):
            raise serializers.ValidationError(
                "The number of authors in the order list does not match the number of "
                "authors in the database."
            )
        if set(order_list) != set(author.id for author in authors):
            raise serializers.ValidationError(
                "The author IDs in the order list do not match the author IDs in the "
                "database."
            )
        author_dict = {author.id: author for author in authors}

        with transaction.atomic():
            for idx, author_id in enumerate(order_list, start=1):
                author = author_dict.get(author_id)
                if author:
                    author.order = idx

            RfcAuthor.objects.bulk_update(authors, ["order"])

        return Response({"status": "RfcAuthor order updated"})


@extend_schema_with_draft_name()
class RpcRelatedDocumentViewSet(viewsets.ModelViewSet):
    queryset = RpcRelatedDocument.objects.all()
    serializer_class = RpcRelatedDocumentSerializer

    def get_queryset(self):
        return (
            super().get_queryset().filter(source__draft__name=self.kwargs["draft_name"])
        )


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


@extend_schema_with_draft_name(actions=["list", "create", "update", "partial_update"])
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
        if dt_person is None:
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


class PaginationPassthroughWrapper:
    """Helper class to make a paginated upstream result work like a queryset for DRF

    Works with a LimitOffsetPagination result the default structure but only cares that
    it contains a .count member with the total number of results available and a
    .results member with the current page of results. The limit and offset that were
    used for the upstream pagination _must_ be the same as the limit and offset used
    for the downstream pagination or this will give nonsense results.

    Exposes the .count as a `.count()` method and passes indexing operations through
    to the .results list, adjusting the indexes to compensate for the offset that was
    already applied.
    """

    def __init__(self, data, total_count, offset):
        self._data = data
        self._total_count = total_count
        self._offset = offset

    def count(self):
        return self._total_count

    def __getitem__(self, item):
        # Pass item lookups through to the results from upstream.
        # Because this was already
        # paginated, remove the offset. LimitOffsetPagination only ever uses
        # queryset[offset:offset+limit],
        # so we don't need to implement esoteric corner cases. Offset and limit
        # are always non-negative.
        if isinstance(item, slice):
            # A slice represents `results[start:stop:step]` - subtract offset from
            # start and stop
            if (item.start is not None and item.start < 0) or (
                item.stop is not None and item.stop < 0
            ):
                raise NotImplementedError("Negative indexing not supported")
            adjusted_item = slice(
                None if item.start is None else item.start - self._offset,
                None if item.stop is None else item.stop - self._offset,
                item.step,
            )
        else:
            # Other than a slice is a single index lookup.  Don't need to support
            # this, but it's easy enough.
            if item < 0:
                raise NotImplementedError("Negative indexing not supported")
            adjusted_item = item - self._offset
        return self._data[adjusted_item]


class SearchDatatrackerPersonsPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


@dataclass
class DatatrackerPersonModelShim:
    """Stand-in for a DatatrackerPerson using results from the search_person() API"""

    datatracker_id: int
    plain_name: str
    picture: str

    @classmethod
    def from_rpcapi_person(cls, obj: rpcapi_client.models.person.Person):
        return cls(
            datatracker_id=obj.id,
            plain_name=obj.plain_name,
            picture=obj.picture,
        )


@extend_schema_view(get=extend_schema(operation_id="search_datatrackerpersons"))
class SearchDatatrackerPersons(ListAPIView):
    """Datatracker person search API

    Search for a datatracker person by name/email fragment.
    """

    # Warning: this is a tricky view!
    #
    # Rather than querying the database, the `get_queryset()` method makes a
    # datatracker API call
    # to perform the Person search. It uses the same pagination limit/offset on the
    # API call as the
    # downstream request being handled. The paginated results from the API call are
    # packaged in
    # the PaginationPassthroughWrapper. This acts as a shim to let DRF's pagination
    # internals work
    # with the already-paginated results as though they came from a local database
    # lookup.
    #
    # Note that despite the naming, DRF APIViews and pagination explicitly support
    # using a list
    # rather than a Django queryset. We need the shim because the list we get from
    # the API only
    # contains a single page of results.

    serializer_class = BaseDatatrackerPersonSerializer
    pagination_class = SearchDatatrackerPersonsPagination

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            # Be sure we don't make an API call during schema generation
            return DatatrackerPerson.objects.none()
        offset = self.paginator.get_offset(self.request)
        upstream_results = self.upstream_search(
            search=self.request.GET.get("search", ""),
            limit=self.paginator.get_limit(self.request),
            offset=offset,
        )
        return PaginationPassthroughWrapper(
            data=[
                DatatrackerPersonModelShim.from_rpcapi_person(r)
                for r in upstream_results.results
            ],
            total_count=upstream_results.count,
            offset=offset,
        )

    @with_rpcapi
    def upstream_search(
        self, search, limit, offset, *, rpcapi: rpcapi_client.DefaultApi
    ):
        return rpcapi.search_person(search=search, limit=limit, offset=offset)
