# Copyright The IETF Trust 2024, All Rights Reserved
"""Build-mode Django settings for RPC project

These are minimal settings to allow management commands to run during
Docker builds. They are NOT intended to be used when actually running
the application.
"""

import os

from .base import *

if os.environ.get("PURPLE_DEPLOYMENT_MODE", "production") != "build":
    raise RuntimeError("build settings are only for use when building")
