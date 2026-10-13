# Copyright The IETF Trust 2026, All Rights Reserved
from django.urls import path

from . import api

# Full paths, so this module also serves as the URLconf for the analytics schema.
urlpatterns = [
    path("api/analytics/documents/", api.DocumentList.as_view()),
    path("api/analytics/staff/", api.StaffList.as_view()),
    path("api/analytics/labels/", api.LabelList.as_view()),
    path("api/analytics/source-formats/", api.SourceFormatList.as_view()),
    path("api/analytics/roles/", api.RoleList.as_view()),
    path("api/analytics/dispositions/", api.DispositionList.as_view()),
    path("api/analytics/schema/", api.SchemaView.as_view()),
]
