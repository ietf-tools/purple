from rest_framework import serializers

from .models import Errata


class ErrataSerializer(serializers.ModelSerializer):
    """Serializer for Errata model"""

    class Meta:
        model = Errata
        fields = [
            "id",
            "rfc_to_be",
            "status",
            "type",
            "section",
            "orig_text",
            "corrected_text",
            "submitter_name",
            "submitter_email",
            "submitter_dt_person",
            "submitted_at",
            "verified_at",
            "verifier_dt_person",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "rfc_to_be",
            "created_at",
            "updated_at",
            "submitted_at",
        ]
