# Copyright The IETF Trust 2026, All Rights Reserved
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from rpc.models import (
    Assignment,
    DispositionName,
    Label,
    RfcToBe,
    RpcPerson,
    RpcRole,
    SourceFormatName,
)


class AnalyticsAssignmentSerializer(serializers.ModelSerializer):
    """A role on a document and the staff member holding it"""

    role_name = serializers.CharField(source="role.name", read_only=True)
    staff_datatracker_id = serializers.IntegerField(
        source="person.datatracker_person.datatracker_id",
        read_only=True,
        allow_null=True,
        help_text="Datatracker person ID; null while nobody is assigned.",
    )
    staff_name = serializers.SerializerMethodField(
        help_text="Null while nobody is assigned."
    )

    class Meta:
        model = Assignment
        fields = ["role", "role_name", "state", "staff_datatracker_id", "staff_name"]
        read_only_fields = fields

    def get_staff_name(self, assignment) -> str | None:
        if assignment.person is None:
            return None
        return self.context["name_map"].get(
            assignment.person.datatracker_person.datatracker_id
        )


class AnalyticsDocumentSerializer(serializers.ModelSerializer):
    """A document handled by the RPC, in any disposition"""

    draft_name = serializers.CharField(
        source="draft.name",
        read_only=True,
        allow_null=True,
        help_text="Null for documents without a draft, such as April 1st RFCs.",
    )
    draft_rev = serializers.CharField(
        source="rev",
        read_only=True,
        help_text="Revision of the draft the RPC works on.",
    )
    draft_datatracker_id = serializers.IntegerField(
        source="draft.datatracker_id", read_only=True, allow_null=True
    )
    disposition_name = serializers.CharField(source="disposition.name", read_only=True)
    source_format = serializers.CharField(
        source="submitted_format_id",
        read_only=True,
        help_text="Slug of the format the document was submitted in.",
    )
    source_format_name = serializers.CharField(
        source="submitted_format.name", read_only=True
    )
    cluster = serializers.IntegerField(
        source="cluster_number",
        read_only=True,
        allow_null=True,
        help_text="Number of the cluster the document belongs to.",
    )
    labels = serializers.SerializerMethodField(help_text="Slugs of applied labels.")
    assignments = AnalyticsAssignmentSerializer(
        source="assignment_set", many=True, read_only=True
    )

    class Meta:
        model = RfcToBe
        fields = [
            "draft_name",
            "draft_rev",
            "draft_datatracker_id",
            "rfc_number",
            "disposition",
            "disposition_name",
            "published_at",
            "source_format",
            "source_format_name",
            "pages",
            "cluster",
            "labels",
            "assignments",
        ]
        read_only_fields = fields

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_labels(self, rfctobe):
        return [label.slug for label in rfctobe.labels.all()]


class AnalyticsStaffSerializer(serializers.ModelSerializer):
    """An RPC staff member, current or former"""

    name = serializers.SerializerMethodField()
    datatracker_person_id = serializers.IntegerField(
        source="datatracker_person.datatracker_id", read_only=True
    )

    class Meta:
        model = RpcPerson
        fields = ["name", "datatracker_person_id", "is_active"]
        read_only_fields = fields

    def get_name(self, rpc_person) -> str | None:
        return self.context["name_map"].get(
            rpc_person.datatracker_person.datatracker_id
        )


class AnalyticsLabelSerializer(serializers.ModelSerializer):
    """A label that can be applied to documents"""

    slug = serializers.CharField(read_only=True)
    name = serializers.CharField(source="text", read_only=True)

    class Meta:
        model = Label
        fields = ["slug", "name", "used"]
        read_only_fields = fields


class AnalyticsSourceFormatSerializer(serializers.ModelSerializer):
    """A format a document can be submitted in"""

    class Meta:
        model = SourceFormatName
        fields = ["slug", "name", "used"]
        read_only_fields = fields


class AnalyticsRoleSerializer(serializers.ModelSerializer):
    """A role a staff member can hold on a document"""

    class Meta:
        model = RpcRole
        fields = ["slug", "name"]
        read_only_fields = fields


class AnalyticsDispositionSerializer(serializers.ModelSerializer):
    """A lifecycle state of a document"""

    class Meta:
        model = DispositionName
        fields = ["slug", "name", "used"]
        read_only_fields = fields
