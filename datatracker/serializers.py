# Copyright The IETF Trust 2025, All Rights Reserved

from rest_framework import serializers


class MergeAuthorSerializer(serializers.Serializer):
    old_person_id = serializers.SerializerMethodField()
    new_person_id = serializers.SerializerMethodField()
