# Copyright The IETF Trust 2024, All Rights Reserved
"""Django settings"""

import os

DEPLOYMENT_MODE = os.environ.get("PURPLE_DEPLOYMENT_MODE", "production")
if DEPLOYMENT_MODE == "development":
    from .development import *
elif DEPLOYMENT_MODE == "build":
    from .build import *
else:
    from .production import *
