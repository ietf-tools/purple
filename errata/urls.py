from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api

router = DefaultRouter()
router.register(r"errata", api.ErratumViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
