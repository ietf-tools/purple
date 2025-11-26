# Copyright The IETF Trust 2025, All Rights Reserved

# Ensure shared_task always finds the correct app
from .celery import app as celery_app

__all__ = ("celery_app",)
