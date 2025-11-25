# Copyright The IETF Trust 2025, All Rights Reserved

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "celery_task_console": {
            "class": "logging.StreamHandler",
            "formatter": "celery_task",
        },
    },
    "formatters": {
        "default": {
            "class": "utils.log.JsonFormatter",
            "style": "{",
            "format": (
                "{asctime}{levelname}{message}{name}{pathname}"
                "{lineno}{funcName}{process}"
            ),
        },
        "celery_task": {
            "()": "utils.log.CeleryTaskJsonFormatter",
            "style": "{",
            "format": (
                "{asctime}{levelname}{message}{name}{pathname}"
                "{lineno}{funcName}{process}{task_id}{task_name}"
            ),
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "celery.task": {
            "handlers": ["celery_task_console"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}
