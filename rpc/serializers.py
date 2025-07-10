# Copyright The IETF Trust 2023-2025, All Rights Reserved

import datetime
import warnings
from dataclasses import dataclass
from itertools import pairwise
from urllib.parse import urljoin

from django.conf import settings
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.fields import empty
from simple_history.models import ModelDelta
from simple_history.utils import update_change_reason

from datatracker.models import DatatrackerPerson, Document

from .models import (
    ActionHolder,
    Assignment,
    Capability,
    Cluster,
    ClusterMember,
    DispositionName,
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
)


class VersionInfoSerializer(serializers.Serializer):
    """Serialize version information"""

    version = serializers.CharField(read_only=True)
    dump_timestamp = serializers.DateTimeField(required=False, read_only=True)


class BaseDatatrackerPersonSerializer(serializers.ModelSerializer):
    """Serialize a minimal DatatrackerPerson

    This is the serializer to use if you may be working with non-persisted
    DatatrackerPerson instances.
    """

    person_id = serializers.IntegerField(source="datatracker_id")
    name = serializers.CharField(source="plain_name", read_only=True)

    class Meta:
        model = DatatrackerPerson
        fields = ["person_id", "name", "picture"]
        read_only_fields = ["picture"]


class DatatrackerPersonSerializer(BaseDatatrackerPersonSerializer):
    """Serializer a DatatrackerPerson, including all the bells and whistles"""

    class Meta(BaseDatatrackerPersonSerializer.Meta):
        fields = BaseDatatrackerPersonSerializer.Meta.fields + ["rpcperson"]
        read_only_fields = BaseDatatrackerPersonSerializer.Meta.read_only_fields + [
            "rpcperson"
        ]


@dataclass
class HistoryRecord:
    id: int
    date: datetime.datetime
    by: DatatrackerPerson | None
    desc: str

    @classmethod
    def from_simple_history(cls, sh, desc):
        dt_person = (
            None if sh.history_user is None else sh.history_user.datatracker_person()
        )
        return cls(
            id=sh.id,
            date=sh.history_date,
            by=dt_person,
            desc=desc,
        )


class HistoryListSerializer(serializers.ListSerializer):
    def describe_model_delta(self, delta: ModelDelta):
        method = (
            getattr(self.parent, "describe_model_delta", None) if self.parent else None
        )
        if method is None:
            return (
                f"{change.field} changed from {change.old} to {change.new}"
                for change in delta.changes
            )
        return method(delta)

    def to_representation(self, data):
        records = []
        model_histories = list(data.all())
        if len(model_histories) > 0:
            for newer, older in pairwise(model_histories):
                parts = []
                if newer.history_change_reason:
                    parts.append(newer.history_change_reason)
                delta = newer.diff_against(older)
                if len(delta.changes) > 0:
                    parts.extend(self.describe_model_delta(delta))
                if len(parts) > 0:
                    records.append(
                        HistoryRecord.from_simple_history(newer, "; ".join(parts))
                    )
            # Always include first history
            first = model_histories[-1]
            records.append(
                HistoryRecord.from_simple_history(
                    first, first.history_change_reason or "Record created"
                )
            )
        return super().to_representation(records)


class HistorySerializer(serializers.Serializer):
    """Serialize a HistoricalRecord"""

    id = serializers.IntegerField()
    time = serializers.DateTimeField(source="date")
    by = DatatrackerPersonSerializer()
    desc = serializers.CharField()

    class Meta:
        list_serializer_class = HistoryListSerializer

    def __init__(self, instance=None, data=empty, **kwargs):
        if not kwargs.get("read_only", True):
            warnings.warn(
                RuntimeWarning(
                    f"{self.__class__} initialized with read_only=False, which is not "
                    "supported. Ignoring."
                ),
                stacklevel=2,
            )
        kwargs["read_only"] = True
        super().__init__(instance, data, **kwargs)


class HistoryLastEditSerializer(serializers.Serializer):
    """Serialize the most recent change in a HistoricalRecord"""

    by = DatatrackerPersonSerializer(
        source="history_user.datatracker_person", read_only=True
    )
    time = serializers.DateTimeField(source="history_date", read_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        if not kwargs.get("read_only", True):
            warnings.warn(
                RuntimeWarning(
                    f"{self.__class__} initialized with read_only=False, which is not "
                    "supported. Ignoring."
                ),
                stacklevel=2,
            )
        kwargs["read_only"] = True
        super().__init__(instance, data, **kwargs)


class RfcAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RfcAuthor
        fields = [
            "id",
            "titlepage_name",
            "is_editor",
            "datatracker_person",
        ]
        read_only_fields = ["id", "datatracker_person"]


class CreateRfcAuthorSerializer(RfcAuthorSerializer):
    class Meta(RfcAuthorSerializer.Meta):
        read_only_fields = ["id"]


class AuthorOrderSerializer(serializers.Serializer):
    order = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of RfcAuthor IDs in the desired order",
    )


class RfcToBeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    rev = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    stream = serializers.SerializerMethodField()
    pages = serializers.SerializerMethodField()
    cluster = serializers.SerializerMethodField()
    # Need to explicitly specify labels as a PK because it uses a through model
    labels = serializers.PrimaryKeyRelatedField(many=True, queryset=Label.objects.all())
    history = HistorySerializer(many=True, read_only=True)
    authors = RfcAuthorSerializer(many=True)

    class Meta:
        model = RfcToBe
        fields = [
            "id",
            "draft",
            "name",
            "rev",
            "title",
            "stream",
            "pages",
            "disposition",
            "external_deadline",
            "internal_goal",
            "labels",
            "cluster",
            "submitted_format",
            "submitted_boilerplate",
            "submitted_std_level",
            "submitted_stream",
            "intended_boilerplate",
            "intended_std_level",
            "intended_stream",
            "history",
            "authors",
        ]
        read_only_fields = ["id", "draft"]

    def get_name(self, rfc_to_be) -> str:
        return (
            rfc_to_be.draft.name if rfc_to_be.draft else "Some Apr 1 RFC"
        )  # TODO: reconcile when we teach the app to handle Apr 1 RFCs

    def get_rev(self, rfc_to_be) -> str:
        return (
            rfc_to_be.draft.rev if rfc_to_be.draft else "none"
        )  # TODO: reconcile when we teach the app to handle Apr 1 RFCs

    def get_title(self, rfc_to_be) -> str:
        return (
            rfc_to_be.draft.title if rfc_to_be.draft else "Some Apr 1 RFC"
        )  # TODO: reconcile when we teach the app to handle Apr 1 RFCs

    def get_stream(self, rfc_to_be) -> str:
        return (
            rfc_to_be.draft.stream if rfc_to_be.draft else "ISE"
        )  # TODO: reconcile when we teach the app to handle Apr 1 RFCs

    def get_pages(self, rfc_to_be) -> int:
        return (
            rfc_to_be.draft.pages if rfc_to_be.draft else 0
        )  # TODO: reconcile when we teach the app to handle Apr 1 RFCs

    def get_cluster(self, rfc_to_be) -> int | None:
        if rfc_to_be.draft:
            cluster = rfc_to_be.draft.cluster_set.first()
            return None if cluster is None else cluster.number
        return None  # RfcToBe without draft cannot be a cluster member

    def create(self, validated_data):
        inst = super().create(validated_data)
        update_change_reason(inst, "Added to the queue")
        return inst

    def describe_model_delta(self, delta: ModelDelta):
        for change in delta.changes:
            if change.field == "labels":
                old = set(delta.old_record.labels.values_list("label__pk", flat=True))
                new = set(delta.new_record.labels.values_list("label__pk", flat=True))
                added = new - old
                removed = old - new
                changes = []
                hist_labels = Label.history.as_of(delta.new_record.history_date)
                if added:
                    added_strs = [
                        f'"{label.slug}"' for label in hist_labels.filter(id__in=added)
                    ]
                    changes.append(
                        f"Added label{'s' if len(added_strs) > 1 else ''} "
                        f"{', '.join(added_strs)}"
                    )
                if removed:
                    removed_strs = [
                        f'"{label.slug}"'
                        for label in hist_labels.filter(id__in=removed)
                    ]
                    changes.append(
                        f"Removed label{'s' if len(removed_strs) > 1 else ''} "
                        f"{', '.join(removed_strs)}"
                    )
                yield " and ".join(changes)
            else:
                yield f'Changed {change.field} from "{change.old}" to "{change.new}"'


class CreateRfcToBeSerializer(serializers.ModelSerializer):
    """Serializer for RfcToBe fields that need to be specified explicitly on import"""

    # Need to explicitly specify labels as a PK because it uses a through model
    labels = serializers.PrimaryKeyRelatedField(many=True, queryset=Label.objects.all())

    class Meta:
        model = RfcToBe
        fields = [
            "submitted_format",
            "submitted_boilerplate",
            "submitted_std_level",
            "submitted_stream",
            "external_deadline",
            "labels",
            "draft",
        ]

    def create(self, validated_data):
        extra_data = {
            "disposition": DispositionName.objects.get(slug="created"),
            "intended_boilerplate": validated_data["submitted_boilerplate"],
            "intended_std_level": validated_data["submitted_std_level"],
            "intended_stream": validated_data["submitted_stream"],
            "internal_goal": validated_data["external_deadline"],
        }
        # default to intended_* == submitted_*
        for field_name in ["boilerplate", "std_level", "stream"]:
            extra_data[f"intended_{field_name}"] = validated_data[
                f"submitted_{field_name}"
            ]
        inst = super().create(validated_data | extra_data)
        update_change_reason(inst, "Added to the queue")
        return inst


class RpcRelatedDocumentSerializer(serializers.ModelSerializer):
    """Serializer for related document for an RfcToBe"""

    target_draft_name = serializers.SerializerMethodField()

    class Meta:
        model = RpcRelatedDocument
        fields = ["id", "relationship", "target_draft_name"]

    def get_target_draft_name(self, obj: RpcRelatedDocument) -> str:
        if obj.target_document is not None:
            return obj.target_document.name
        return obj.target_rfctobe.draft.name


class CreateRpcRelatedDocumentSerializer(RpcRelatedDocumentSerializer):
    """Serializer for creating a related document for an RfcToBe"""

    target_draft_name = serializers.CharField(write_only=True)

    class Meta(RpcRelatedDocumentSerializer.Meta):
        fields = ["id", "relationship", "source", "target_draft_name"]

    def create(self, validated_data):
        target_draft_name = validated_data.pop("target_draft_name")

        source = validated_data["source"]

        target_document = Document.objects.filter(name=target_draft_name).first()
        target_rfctobe = None
        if not target_document:
            target_rfctobe = RfcToBe.objects.filter(
                draft__name=target_draft_name
            ).first()
            if not target_rfctobe:
                raise serializers.ValidationError(
                    f"No Document or RfcToBe found for draft name '{target_draft_name}'"
                )

        try:
            related_doc = RpcRelatedDocument.objects.create(
                relationship=validated_data["relationship"],
                source=source,
                target_document=target_document,
                target_rfctobe=target_rfctobe,
            )
        except IntegrityError as err:
            raise serializers.ValidationError(
                f"Failed to create related document due to a database constraint: {err}"
            ) from err

        return related_doc


class CapabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Capability
        fields = ["slug", "name", "desc"]


class RpcRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RpcRole
        fields = ["slug", "name", "desc"]


class RpcPersonSerializer(serializers.ModelSerializer):
    """Serialize an RpcPerson

    To avoid datatracker API calls, use the `name_map` parameter to
    pass a dict mapping datatracker Person ID to name (designed for use
    with the `get_persons()` API endpoint).
    """

    name = serializers.SerializerMethodField()
    capabilities = CapabilitySerializer(source="capable_of", many=True)
    roles = RpcRoleSerializer(source="can_hold_role", many=True)

    class Meta:
        model = RpcPerson
        fields = ["id", "name", "hours_per_week", "capabilities", "roles", "is_active"]

    def __init__(self, *args, **kwargs):
        context = kwargs.get("context", {})
        self.name_map: dict[int, str] = context.pop(
            "name_map", {}
        )  # datatracker_id -> name
        super().__init__(*args, **kwargs)

    def get_name(self, rpc_person) -> str:
        cached_name = self.name_map.get(
            rpc_person.datatracker_person.datatracker_id, None
        )
        return cached_name or rpc_person.datatracker_person.plain_name


class ActionHolderSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = ActionHolder
        fields = [
            "name",
            "deadline",
            "since_when",
            "comment",
        ]

    def get_name(self, actionholder) -> str:
        return actionholder.datatracker_person.plain_name  # allow prefetched name map?


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = [
            "id",
            "rfc_to_be",
            "person",
            "role",
            "state",
            "comment",
            "time_spent",
        ]


class NestedAssignmentSerializer(AssignmentSerializer):
    rfc_to_be = RfcToBeSerializer(read_only=True)


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = [
            "id",
            "slug",
            "is_exception",
            "is_complexity",
            "color",
        ]


class QueueItemSerializer(RfcToBeSerializer):
    labels = LabelSerializer(many=True, read_only=True)
    assignment_set = AssignmentSerializer(
        source="assignment_set.active", many=True, read_only=True
    )
    actionholder_set = ActionHolderSerializer(
        source="actionholder_set.active", many=True, read_only=True
    )
    requested_approvals = serializers.SerializerMethodField()

    class Meta(RfcToBeSerializer.Meta):
        fields = RfcToBeSerializer.Meta.fields + [
            "labels",
            "assignment_set",
            "actionholder_set",
            "requested_approvals",
        ]

    def get_requested_approvals(self, rfc_to_be) -> list:
        return []  # todo return a value


class ClusterMemberListSerializer(serializers.ListSerializer):
    """ListSerializer for ClusterMembers to allow multiple updates

    This is a place-holder for implementations of write operations in the Cluster
    API. If we take the approach of create/update operations entirely setting and
    replacing the set of ClusterMembers, then the methods here are the place to
    implement those.

    If we go in a different direction, we could do away with this and let the
    ClusterMemberSerializer use the default `ListSerializer` class.

    https://www.django-rest-framework.org/api-guide/serializers/#customizing-listserializer-behavior
    """

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance: list[ClusterMember], validated_data):
        raise NotImplementedError


class ClusterMemberSerializer(serializers.Serializer):
    name = serializers.CharField(source="doc.name")
    rfc_number = serializers.SerializerMethodField()

    class Meta:
        model = ClusterMember
        list_serializer_class = ClusterMemberListSerializer

    def get_rfc_number(self, clustermember: ClusterMember) -> int | None:
        try:
            rfctobe = RfcToBe.objects.get(draft=clustermember.doc)
        except RfcToBe.DoesNotExist:
            return None
        return rfctobe.rfc_number


class ClusterSerializer(serializers.ModelSerializer):
    """Serialize a Cluster instance

    Uses a nested representation for `documents` rather than the ModelSerializer's
    handling of relations so we can work with the through model. Specifically, we
    want to respect the `order_by` setting of the `ClusterMember` class.
    """

    documents = ClusterMemberSerializer(source="clustermember_set", many=True)

    class Meta:
        model = Cluster
        fields = [
            "number",
            "documents",
        ]


class SourceFormatNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceFormatName
        fields = ["slug", "name", "desc"]


class StdLevelNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = StdLevelName
        fields = ["slug", "name", "desc"]


class StreamNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamName
        fields = ["slug", "name", "desc"]


class TlpBoilerplateChoiceNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceFormatName
        fields = ["slug", "name", "desc"]


@dataclass
class SubmissionAuthor:
    id: int
    plain_name: str

    @classmethod
    def from_rpcapi_draft_author(cls, author):
        return cls(id=author.person, plain_name=author.plain_name)


@dataclass
class Submission:
    id: int
    name: str
    rev: str
    stream: StreamName
    title: str
    pages: int
    source_format: SourceFormatName
    authors: list[SubmissionAuthor]
    shepherd: str
    std_level: StdLevelName | None
    datatracker_url: str

    @classmethod
    def from_rpcapi_draft(cls, draft):
        return cls(
            id=draft.id,
            name=draft.name,
            rev=draft.rev,
            stream=StreamName.objects.from_slug(draft.stream),
            title=draft.title,
            pages=draft.pages,
            source_format=SourceFormatName.objects.get(slug=draft.source_format),
            authors=[
                SubmissionAuthor.from_rpcapi_draft_author(a) for a in draft.authors
            ],
            shepherd=draft.shepherd,
            std_level=(
                StdLevelName.objects.from_slug(draft.intended_std_level)
                if draft.intended_std_level
                else None
            ),
            datatracker_url=urljoin(
                settings.DATATRACKER_BASE, f"/doc/{draft.name}-{draft.rev}"
            ),
        )


class SubmissionAuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    plain_name = serializers.CharField()


class SubmissionSerializer(serializers.Serializer):
    """Serialize a submission"""

    id = serializers.IntegerField()
    name = serializers.CharField()
    rev = serializers.CharField()
    stream = StreamNameSerializer()
    title = serializers.CharField()
    pages = serializers.IntegerField()
    source_format = SourceFormatNameSerializer()
    authors = SubmissionAuthorSerializer(many=True)
    shepherd = serializers.EmailField()
    std_level = StdLevelNameSerializer(required=False)
    datatracker_url = serializers.URLField()


class SubmissionListItemSerializer(serializers.Serializer):
    """Serialize a submission list item

    Only includes a subset of the SubmissionSerializer fields
    """

    id = serializers.IntegerField()
    name = serializers.CharField()
    stream = serializers.CharField()
    submitted = serializers.DateTimeField()


def check_user_has_role(user, role) -> bool:
    rpc_person = RpcPerson.objects.filter(
        datatracker_person=user.datatracker_person()
    ).first()
    if rpc_person:
        return rpc_person.can_hold_role.filter(slug=role).exists()
    return False


class DocumentCommentSerializer(serializers.ModelSerializer):
    """Serialize a comment on an RfcToBe"""

    by = DatatrackerPersonSerializer(read_only=True)
    last_edit = HistoryLastEditSerializer(read_only=True)

    class Meta:
        model = RpcDocumentComment
        fields = [
            "id",
            "comment",
            "by",
            "time",
            "last_edit",
        ]
        read_only_fields = ["rfc_to_be", "by", "time"]
