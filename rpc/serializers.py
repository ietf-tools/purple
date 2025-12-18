# Copyright The IETF Trust 2023-2025, All Rights Reserved

import datetime
import warnings
from dataclasses import dataclass
from itertools import pairwise

import rpcapi_client
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.fields import empty
from simple_history.models import ModelDelta
from simple_history.utils import update_change_reason

from datatracker.models import DatatrackerPerson, Document
from datatracker.rpcapi import with_rpcapi
from datatracker.utils import build_datatracker_url

from .models import (
    ActionHolder,
    ApprovalLogMessage,
    Assignment,
    BlockingReason,
    Capability,
    Cluster,
    ClusterMember,
    DispositionName,
    DocRelationshipName,
    FinalApproval,
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
    SubseriesMember,
    UnusableRfcNumber,
)


class VersionInfoSerializer(serializers.Serializer):
    """Serialize version information"""

    version = serializers.CharField(read_only=True)
    dump_timestamp = serializers.DateTimeField(required=False, read_only=True)


class NameSerializer(serializers.Serializer):
    """Serialize any Name subclass"""

    slug = serializers.CharField(max_length=32)
    name = serializers.CharField(max_length=255)
    desc = serializers.CharField(allow_blank=True)
    used = serializers.BooleanField(default=True)


class BaseDatatrackerPersonSerializer(serializers.ModelSerializer):
    """Serialize a minimal DatatrackerPerson

    This is the serializer to use if you may be working with non-persisted
    DatatrackerPerson instances.
    """

    person_id = serializers.IntegerField(source="datatracker_id")
    name = serializers.CharField(source="plain_name", read_only=True)
    email = serializers.EmailField(read_only=True)
    picture = serializers.URLField(read_only=True)
    datatracker_url = serializers.URLField(source="url", read_only=True)

    class Meta:
        model = DatatrackerPerson
        fields = ["person_id", "name", "email", "picture", "datatracker_url"]


class DatatrackerPersonSerializer(BaseDatatrackerPersonSerializer):
    """Serializer a DatatrackerPerson, including all the bells and whistles"""

    class Meta(BaseDatatrackerPersonSerializer.Meta):
        fields = BaseDatatrackerPersonSerializer.Meta.fields + ["rpcperson"]
        read_only_fields = ["rpcperson"]


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
    @staticmethod
    def _default_model_change_description(delta):
        return (
            f"{change.field} changed from {change.old} to {change.new}"
            for change in delta.changes
        )

    def describe_model_delta(self, delta: ModelDelta):
        method_name = "describe_model_delta"
        if hasattr(self.parent, method_name):
            method = getattr(self.parent, method_name)
        elif hasattr(self.child, method_name):
            method = getattr(self.child, method_name)
        else:
            return self._default_model_change_description
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


class ActionHolderSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = ActionHolder
        fields = [
            "name",
            "deadline",
            "since_when",
            "comment",
            "body",
        ]

    def get_name(self, actionholder) -> str:
        return actionholder.datatracker_person.plain_name  # allow prefetched name map?


class AssignmentSerializer(serializers.ModelSerializer):
    """Assignment serializer with PK reference to RfcToBe"""

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

    def to_internal_value(self, data):
        # For partial updates, add "state" field to avoid constraint violations
        if getattr(self, "partial", False) and self.instance:
            if "state" not in data:
                data["state"] = self.instance.state

        return super().to_internal_value(data)


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = [
            "id",
            "slug",
            "is_exception",
            "is_complexity",
            "color",
            "used",
        ]


class RfcAuthorSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="datatracker_person.plain_name", read_only=True)
    email = serializers.EmailField(source="datatracker_person.email", read_only=True)
    picture = serializers.URLField(source="datatracker_person.picture", read_only=True)
    datatracker_url = serializers.URLField(
        source="datatracker_person.url", read_only=True
    )

    class Meta:
        model = RfcAuthor
        fields = [
            "id",
            "name",
            "email",
            "titlepage_name",
            "is_editor",
            "picture",
            "datatracker_url",
        ]

    def update(self, instance, validated_data):
        RfcAuthor.objects.filter(pk=instance.pk).update(**validated_data)
        return RfcAuthor.objects.get(pk=instance.pk)


class CreateRfcAuthorSerializer(RfcAuthorSerializer):
    # person_id is not a field on the model - remove it from validated_data
    # before saving!
    person_id = serializers.IntegerField(
        write_only=True,
        help_text="datatracker ID of a Person",
        required=False,
        allow_null=True,
    )

    class Meta(RfcAuthorSerializer.Meta):
        fields = RfcAuthorSerializer.Meta.fields + ["person_id"]


class AuthorOrderSerializer(serializers.Serializer):
    order = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of RfcAuthor IDs in the desired order",
    )


class RpcRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RpcRole
        fields = ["slug", "name", "desc"]


class DraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "name",
            "rev",
            "title",
            "pages",
        ]
        read_only_fields = fields


class SimpleClusterSerializer(serializers.ModelSerializer):
    """Serialize a cluster without its contents"""

    class Meta:
        model = Cluster
        fields = ["number"]


class ClusterAddRemoveDocumentSerializer(serializers.Serializer):
    """Serializer for adding or removing a document in a cluster"""

    draft_name = serializers.CharField(
        help_text="Name of the draft to add/remove in the cluster"
    )


class ClusterReorderDocumentsSerializer(serializers.Serializer):
    """Serializer for reordering documents in a cluster"""

    draft_names = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of draft names in the desired order",
    )


class MinimalRfcToBeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RfcToBe
        fields = ["name", "rfc_number"]


class FinalApprovalSerializer(serializers.Serializer):
    """Serialize final approval information for an RfcToBe"""

    id = serializers.IntegerField(read_only=True)
    rfc_to_be = MinimalRfcToBeSerializer(read_only=True)
    requested = serializers.DateTimeField(read_only=True)
    approver = BaseDatatrackerPersonSerializer(read_only=True)
    approved = serializers.DateTimeField(required=False, allow_null=True)
    overriding_approver = BaseDatatrackerPersonSerializer(
        allow_null=True, read_only=True
    )
    approver_person_id = serializers.IntegerField(write_only=True, required=False)
    overriding_approver_person_id = serializers.IntegerField(
        write_only=True, required=False
    )

    def update(self, instance, validated_data):
        approver_person_id = validated_data.pop("approver_person_id", None)
        approver_dt_person = None
        if approver_person_id:
            approver_dt_person = DatatrackerPerson.objects.get(
                datatracker_id=approver_person_id
            )

        overriding_approver_person_id = validated_data.pop(
            "overriding_approver_person_id", None
        )
        overriding_approver_dt_person = None
        if overriding_approver_person_id:
            overriding_approver_dt_person = DatatrackerPerson.objects.get(
                datatracker_id=overriding_approver_person_id
            )

        FinalApproval.objects.filter(pk=instance.pk).update(
            overriding_approver=overriding_approver_dt_person,
            approver=approver_dt_person,
            **validated_data,
        )
        return FinalApproval.objects.get(pk=instance.pk)


class IanaStatusSerializer(NameSerializer):
    """Serialize IANA status with slug and display text"""

    def to_representation(self, instance):
        """Convert the stored slug value to an object with slug and desc"""
        choices_dict = dict(RfcToBe.IanaStatus.choices)
        return {
            "slug": instance,
            "name": instance,
            "desc": choices_dict.get(instance, instance),
        }


class BlockingReasonSerializer(NameSerializer):
    """Serialize BlockingReason model"""

    class Meta:
        model = BlockingReason
        fields = ["slug", "name", "desc"]


class RfcToBeBlockingReasonSerializer(serializers.Serializer):
    """Serialize RfcToBeBlockingReason with reason details"""

    reason = BlockingReasonSerializer(read_only=True)
    since_when = serializers.DateTimeField(read_only=True)
    resolved = serializers.DateTimeField(read_only=True)


class QueueItemSerializer(serializers.ModelSerializer):
    """RfcToBe serializer suitable for displaying a queue of many"""

    pages = serializers.IntegerField(source="draft.pages", read_only=True)
    cluster = SimpleClusterSerializer(read_only=True)
    labels = LabelSerializer(many=True, read_only=True)
    assignment_set = AssignmentSerializer(
        source="active_assignments", many=True, read_only=True
    )
    actionholder_set = ActionHolderSerializer(
        source="active_actionholders", many=True, read_only=True
    )
    pending_activities = RpcRoleSerializer(many=True, read_only=True)
    enqueued_at = serializers.SerializerMethodField()
    final_approval = FinalApprovalSerializer(
        source="finalapproval_set", many=True, read_only=True
    )
    iana_status = IanaStatusSerializer(read_only=True)
    blocking_reasons = serializers.SerializerMethodField()

    class Meta:
        model = RfcToBe
        fields = [
            "id",
            "name",
            "pages",
            "disposition",
            "external_deadline",
            "internal_goal",
            "labels",
            "cluster",
            "assignment_set",
            "actionholder_set",
            "pending_activities",
            "rfc_number",
            "pages",
            "enqueued_at",
            "final_approval",
            "iana_status",
            "blocking_reasons",
        ]

    @extend_schema_field(serializers.DateField())
    def get_enqueued_at(self, obj):
        """Get the date when the RFC was added to the queue"""
        # Use annotated value if present to avoid per-row history queries
        annotated = getattr(obj, "enqueued_at", None)
        if annotated is not None:
            return annotated
        try:
            create_history = obj.history.filter(history_type="+").earliest(
                "history_date"
            )
            return create_history.history_date
        except obj.history.model.DoesNotExist:
            # Fallback if no history exists
            return None

    @extend_schema_field(RfcToBeBlockingReasonSerializer(many=True))
    def get_blocking_reasons(self, obj):
        """Get active blocking reasons for this RfcToBe"""
        active_reasons = obj.rfctobeblockingreason_set.filter(
            resolved__isnull=True
        ).select_related("reason")
        return RfcToBeBlockingReasonSerializer(active_reasons, many=True).data


class SubseriesMemberSerializer(serializers.ModelSerializer):
    """Serialize a SubseriesMember"""

    display_name = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    class Meta:
        model = SubseriesMember
        fields = ["id", "rfc_to_be", "type", "number", "display_name", "slug"]

    def get_display_name(self, obj) -> str:
        if not obj:
            return None
        return f"{obj.type.slug.upper()} {obj.number}"

    def get_slug(self, obj) -> str:
        if not obj:
            return None
        return f"{obj.type.slug.lower()}{obj.number}"


@dataclass
class SubseriesDoc:
    """Representation of a single Subseries Doc (e.g. BCP 123) and its containing
    RFCs"""

    type: str
    number: int

    @property
    def documents(self) -> QuerySet[RfcToBe]:
        return RfcToBe.objects.filter(
            subseriesmember__type__slug=self.type,
            subseriesmember__number=self.number,
        ).prefetch_related("subseriesmember_set")

    @property
    def rfc_count(self) -> int:
        return len(self.documents)

    @property
    def slug(self) -> str:
        return f"{self.type.lower()}{self.number}"

    @property
    def display_name(self) -> str:
        return f"{self.type.upper()} {self.number}"


class SubseriesDocSerializer(serializers.Serializer):
    type = serializers.CharField()
    number = serializers.IntegerField()
    documents = MinimalRfcToBeSerializer(many=True)
    rfc_count = serializers.IntegerField(read_only=True)
    slug = serializers.CharField(read_only=True)
    display_name = serializers.CharField(read_only=True)


class RfcToBeSerializer(serializers.ModelSerializer):
    """RfcToBeSerializer suitable for displaying full details of a single instance"""

    draft = DraftSerializer(read_only=True)
    cluster = SimpleClusterSerializer(read_only=True)
    # Need to explicitly specify labels as a PK because it uses a through model
    labels = serializers.PrimaryKeyRelatedField(many=True, queryset=Label.objects.all())
    authors = RfcAuthorSerializer(many=True)
    assignment_set = AssignmentSerializer(
        source="assignment_set.active", many=True, read_only=True
    )
    actionholder_set = ActionHolderSerializer(
        source="actionholder_set.active", many=True, read_only=True
    )
    pending_activities = RpcRoleSerializer(many=True, read_only=True)
    consensus = serializers.SerializerMethodField()

    subseries = SubseriesMemberSerializer(
        source="subseriesmember_set", many=True, read_only=True
    )
    iana_status = IanaStatusSerializer(read_only=True)

    iana_status_slug = serializers.ChoiceField(
        source="iana_status",
        choices=RfcToBe.IanaStatus.choices,
        write_only=True,
        required=False,
        help_text=("Set the IANA status by providing the slug identifier."),
    )

    class Meta:
        model = RfcToBe
        fields = [
            "id",
            "name",
            "title",
            "draft",
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
            "authors",
            "assignment_set",
            "actionholder_set",
            "pending_activities",
            "rfc_number",
            "published_at",
            "consensus",
            "subseries",
            "iana_status",
            "iana_status_slug",
        ]
        read_only_fields = ["id", "draft", "published_at"]

    def get_consensus(self, obj) -> bool:
        return obj.draft.consensus


class RfcToBeHistorySerializer(HistorySerializer):
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

    iana_status_slug = serializers.ChoiceField(
        source="iana_status",
        choices=RfcToBe.IanaStatus.choices,
        write_only=True,
        required=False,
        help_text="Set the IANA status by providing the slug identifier. "
        "Defaults to 'not_completed' if not provided.",
    )

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
            "iana_status_slug",
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


class NestedAssignmentSerializer(AssignmentSerializer):
    """Assignment serializer with nested RfcToBe details"""

    rfc_to_be = RfcToBeSerializer(read_only=True)


class RpcRelatedDocumentSerializer(serializers.ModelSerializer):
    """Serializer for related document for an RfcToBe"""

    target_draft_name = serializers.SerializerMethodField()
    draft_name = serializers.SerializerMethodField()

    class Meta:
        model = RpcRelatedDocument
        fields = ["id", "relationship", "draft_name", "target_draft_name"]

    def get_target_draft_name(self, obj: RpcRelatedDocument) -> str:
        if obj.target_document is not None:
            return obj.target_document.name
        if obj.target_rfctobe is not None and obj.target_rfctobe.draft is not None:
            return obj.target_rfctobe.draft.name
        return None

    @extend_schema_field(serializers.CharField())
    def get_draft_name(self, obj: RpcRelatedDocument) -> str:
        """Get the draft name of the source document"""
        return obj.source.draft.name


class CreateRpcRelatedDocumentSerializer(RpcRelatedDocumentSerializer):
    """Serializer for creating a related document for an RfcToBe"""

    target_draft_name = serializers.CharField(write_only=True, required=True)
    source = serializers.PrimaryKeyRelatedField(
        queryset=RfcToBe.objects.all(), write_only=True
    )
    # This field is read-only to return the name of the target document;
    # in subsequent "to_representation" it will be renamed to target_draft_name;
    # This hack is required to map the model's fields (doc, rfctobe) to the serializer's
    # fields (target_draft_name)
    target_draft_name_output = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RpcRelatedDocument
        fields = [
            "id",
            "relationship",
            "source",
            "draft_name",
            "target_draft_name",
            "target_draft_name_output",
        ]

    @extend_schema_field(serializers.CharField())
    def get_target_draft_name_output(self, obj):
        if obj.target_document is not None:
            return obj.target_document.name
        if obj.target_rfctobe is not None and obj.target_rfctobe.draft is not None:
            return obj.target_rfctobe.draft.name
        return None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["target_draft_name"] = ret.pop("target_draft_name_output", None)
        # Remove source from response for consistency, cient works with draft_name
        ret.pop("source", None)

        return ret

    def create(self, validated_data):
        target_draft_name = validated_data.pop("target_draft_name")

        source = validated_data["source"]

        target_rfctobe = RfcToBe.objects.filter(draft__name=target_draft_name).first()
        target_document = None
        if not target_rfctobe:
            target_document = Document.objects.filter(name=target_draft_name).first()
            if not target_document:
                raise serializers.ValidationError(
                    f"No Document or RfcToBe found for draft name '{target_draft_name}'"
                )

        try:
            data = {
                "relationship": validated_data["relationship"],
                "source": source,
                "target_document": target_document,
                "target_rfctobe": target_rfctobe,
            }
            related_doc = super().create(data)
        except IntegrityError as err:
            raise serializers.ValidationError(
                f"Failed to create related document due to a database constraint: {err}"
            ) from err

        return related_doc


class CapabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Capability
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
    email = serializers.EmailField(source="datatracker_person.email", read_only=True)
    picture = serializers.URLField(source="datatracker_person.picture", read_only=True)
    datatracker_url = serializers.URLField(
        source="datatracker_person.url", read_only=True
    )

    class Meta:
        model = RpcPerson
        fields = [
            "id",
            "name",
            "hours_per_week",
            "capabilities",
            "roles",
            "is_active",
            "email",
            "picture",
            "datatracker_url",
        ]

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
    disposition = serializers.SerializerMethodField()
    references = serializers.SerializerMethodField()
    is_received = serializers.SerializerMethodField()
    order = serializers.IntegerField()

    class Meta:
        model = ClusterMember
        list_serializer_class = ClusterMemberListSerializer

    def get_rfc_number(self, clustermember: ClusterMember) -> int | None:
        if hasattr(clustermember.doc, "rfctobe_annotated"):
            rfctobes = clustermember.doc.rfctobe_annotated
            if rfctobes:
                return rfctobes[0].rfc_number
            return None

        # fallback to original logic
        rfctobe = clustermember.doc.rfctobe_set.exclude(
            disposition__slug="withdrawn"
        ).first()
        return rfctobe.rfc_number if rfctobe else None

    def get_disposition(self, clustermember: ClusterMember) -> str | None:
        if hasattr(clustermember.doc, "rfctobe_annotated"):
            rfctobes = clustermember.doc.rfctobe_annotated
            if rfctobes:
                return rfctobes[0].disposition.slug
            return None

        # fallback to original logic
        rfctobe = clustermember.doc.rfctobe_set.exclude(
            disposition__slug="withdrawn"
        ).first()
        if rfctobe and rfctobe.disposition:
            return rfctobe.disposition.slug
        return None

    @extend_schema_field(RpcRelatedDocumentSerializer(many=True))
    @with_rpcapi
    def get_references(
        self, clustermember: ClusterMember, rpcapi: rpcapi_client.PurpleApi
    ) -> list[dict] | None:
        """Get related documents for this cluster member"""
        if hasattr(clustermember.doc, "rfctobe_annotated"):
            rfctobes = clustermember.doc.rfctobe_annotated
            rfctobe = rfctobes[0] if rfctobes else None
        else:
            rfctobe = clustermember.doc.rfctobe_set.exclude(
                disposition__slug="withdrawn"
            ).first()

        if not rfctobe:
            # if the doc is not received, get references on-the-fly from dt
            api_references = rpcapi.get_draft_references(
                clustermember.doc.datatracker_id
            )
            if not api_references:
                return None

            references_data = []
            existing_rfc_to_be = dict(
                RfcToBe.objects.filter(
                    draft__datatracker_id__in=[s.id for s in api_references]
                )
                .exclude(disposition__slug="withdrawn")
                .values_list("draft__datatracker_id", "disposition__slug")
            )
            for ref in api_references:
                if not existing_rfc_to_be.get(ref.id):
                    relationship = DocRelationshipName.NOT_RECEIVED_RELATIONSHIP_SLUG
                elif existing_rfc_to_be.get(ref.id) in ("created", "in_progress"):
                    relationship = DocRelationshipName.REFQUEUE_RELATIONSHIP_SLUG
                else:
                    continue
                references_data.append(
                    {
                        "id": None,
                        "relationship": relationship,
                        "draft_name": clustermember.doc.name,
                        "target_draft_name": ref.name,
                    }
                )

            return references_data

        # Check if references are already prefetched
        if hasattr(rfctobe, "references_annotated"):
            related_docs = rfctobe.references_annotated
            if not related_docs:
                return None
            return RpcRelatedDocumentSerializer(related_docs, many=True).data

        related_docs = RpcRelatedDocument.objects.filter(
            source=rfctobe,
            relationship__slug__in=DocRelationshipName.REFERENCE_RELATIONSHIP_SLUGS,
        )

        if not related_docs.exists():
            return None

        return RpcRelatedDocumentSerializer(related_docs, many=True).data

    def get_is_received(self, clustermember: ClusterMember) -> bool | None:
        """Determine if the document has been received based on related documents"""
        if hasattr(clustermember.doc, "rfctobe_annotated"):
            rfctobes = clustermember.doc.rfctobe_annotated
            return bool(rfctobes)

        # fallback to original logic
        return RfcToBe.objects.filter(draft=clustermember.doc).exists()


class ClusterSerializer(serializers.ModelSerializer):
    """Serialize a Cluster instance

    Uses a nested representation for `documents` rather than the ModelSerializer's
    handling of relations so we can work with the through model. Specifically, we
    want to respect the `order_by` setting of the `ClusterMember` class.
    """

    documents = ClusterMemberSerializer(
        source="clustermember_set", many=True, read_only=True
    )
    draft_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="List of draft names to add to the cluster",
    )
    is_active = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cluster
        fields = ["number", "documents", "draft_names", "is_active"]

    def get_is_active(self, cluster) -> bool:
        """A cluster is considered active if it not empty and not all
        drafts in the cluster are published or withdrawn.
        """

        # Use annotated value if available
        if hasattr(cluster, "is_active_annotated"):
            return cluster.is_active_annotated

        member_doc_ids = list(
            ClusterMember.objects.filter(cluster=cluster).values_list(
                "doc_id", flat=True
            )
        )
        if not member_doc_ids:
            return False

        return (
            # if any not published/withdrawn RFC exist in cluster, then active
            RfcToBe.objects.filter(draft_id__in=member_doc_ids)
            .exclude(disposition__slug="published")
            .exclude(disposition__slug="withdrawn")
            .exists()
        )

    def create(self, validated_data):
        draft_names = validated_data.pop("draft_names", [])
        cluster = Cluster.objects.create(number=validated_data["number"])

        if draft_names:
            with transaction.atomic():
                order = 1
                for draft_name in draft_names:
                    # validate if doc exists
                    if not Document.objects.filter(name=draft_name).exists():
                        raise serializers.ValidationError(
                            {
                                "draft_name": f"Document with name '{draft_name}' "
                                "not found"
                            },
                            code="document_not_found",
                        )
                    doc = Document.objects.get(name=draft_name)
                    ClusterMember.objects.create(cluster=cluster, doc=doc, order=order)
                    order += 1

        return cluster

    def update(self, instance, validated_data):
        if "number" in validated_data:
            raise serializers.ValidationError("Cluster number cannot be updated")

        draft_names = validated_data.pop("draft_names", [])
        if draft_names:
            with transaction.atomic():
                ClusterMember.objects.filter(cluster=instance).delete()
                order = 1
                for draft_name in draft_names:
                    # validate if doc exists
                    if not Document.objects.filter(name=draft_name).exists():
                        raise serializers.ValidationError(
                            {
                                "draft_name": f"Document with name '{draft_name}' "
                                "not found"
                            },
                            code="document_not_found",
                        )
                    doc = Document.objects.get(name=draft_name)
                    if ClusterMember.objects.filter(
                        cluster__number=instance.number, doc=doc
                    ).exists():
                        raise serializers.ValidationError(
                            {
                                "draft_name": f"Document with name '{draft_name}' is "
                                f"already in cluster '{instance.number}'"
                            },
                            code="document_already_in_cluster",
                        )
                    ClusterMember.objects.create(cluster=instance, doc=doc, order=order)
                    order += 1

        instance.refresh_from_db()
        return instance


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
    consensus: bool

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
            datatracker_url=build_datatracker_url(f"/doc/{draft.name}-{draft.rev}"),
            consensus=draft.consensus,
        )


class SubmissionAuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    plain_name = serializers.CharField()


class SubmissionSerializer(serializers.Serializer):
    """Serialize a submission"""

    id = serializers.IntegerField()
    name = serializers.CharField()
    rev = serializers.CharField()
    stream = NameSerializer()
    title = serializers.CharField()
    pages = serializers.IntegerField()
    source_format = NameSerializer()
    authors = SubmissionAuthorSerializer(many=True)
    shepherd = serializers.EmailField()
    std_level = NameSerializer(required=False)
    datatracker_url = serializers.URLField()
    consensus = serializers.BooleanField()


class SubmissionListItemSerializer(serializers.Serializer):
    """Serialize a submission list item

    Only includes a subset of the SubmissionSerializer fields
    """

    id = serializers.IntegerField()
    name = serializers.CharField()
    stream = serializers.CharField()
    submitted = serializers.DateTimeField()


def check_user_has_role(user, role) -> bool:
    rpc_person = user.rpcperson() if hasattr(user, "rpcperson") else None
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


class UnusableRfcNumberSerializer(serializers.ModelSerializer):
    """Serialize an Unusable Rfc Number"""

    created_at = serializers.SerializerMethodField()

    class Meta:
        model = UnusableRfcNumber
        fields = ["number", "comment", "created_at"]

    @extend_schema_field(serializers.DateTimeField())
    def get_created_at(self, obj):
        # Get the creation date from history
        first_history = obj.history.filter(history_type="+").first()
        return first_history.history_date if first_history else None


class CreateFinalApprovalSerializer(FinalApprovalSerializer):
    """Serializer for creating FinalApproval instances"""

    approver_person_id = serializers.IntegerField(write_only=True, required=True)
    overriding_approver_person_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )

    def create(self, validated_data):
        approver_person_id = validated_data.pop("approver_person_id")
        overriding_approver_person_id = validated_data.pop(
            "overriding_approver_person_id", None
        )

        approver_dt_person = DatatrackerPerson.objects.get(
            datatracker_id=approver_person_id
        )

        overriding_approver_dt_person = None
        if overriding_approver_person_id:
            overriding_approver_dt_person = DatatrackerPerson.objects.get(
                datatracker_id=overriding_approver_person_id
            )

        return FinalApproval.objects.create(
            approver=approver_dt_person,
            overriding_approver=overriding_approver_dt_person,
            **validated_data,
        )


class MailAttachmentSerializer(serializers.Serializer):
    name = serializers.CharField()
    content = serializers.FileField(
        allow_empty_file=False,
        use_url=False,
    )


class MailMessageSerializer(serializers.Serializer):
    """Mail message serializer

    Because of the FileField, this cannot be used with a JSONParser.
    """

    msgtype = serializers.CharField(help_text="slug that identifies message type ")
    to = serializers.CharField(allow_blank=False)
    cc = serializers.CharField(default="", allow_blank=True)
    subject = serializers.CharField(allow_blank=False)
    body = serializers.CharField(allow_blank=False)
    attachments = MailAttachmentSerializer(many=True, required=False)


class MailTemplateSerializer(serializers.Serializer):
    label = serializers.CharField(help_text="human readable text for UI")
    template = MailMessageSerializer()


class MailResponseSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["success", "error"])
    message = serializers.CharField()


class ApprovalLogMessageSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    by = DatatrackerPersonSerializer(read_only=True)
    rfc_to_be = MinimalRfcToBeSerializer(read_only=True)
    log_message = serializers.CharField()
    time = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        # Set the 'by' field to the current user
        request = self.context.get("request")
        validated_data["by"] = request.user.datatracker_person()

        return ApprovalLogMessage.objects.create(**validated_data)

    def update(self, instance, validated_data):
        ApprovalLogMessage.objects.filter(pk=instance.pk).update(
            **validated_data,
        )
        return ApprovalLogMessage.objects.get(pk=instance.pk)
