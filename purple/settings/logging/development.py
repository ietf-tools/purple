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
            "()": "utils.log.SimpleFormatter",
            "format": "[{asctime}] ({levelname}) {message} ({name})",
            "style": "{",
        },
        "celery_task": {
            "()": "utils.log.CeleryTaskFormatter",
            "format": (
                "[%(asctime)s] (%(levelname)s) "
                "Task %(task_name)s[%(task_id)s] log: %(message)s"
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
            "level": "DEBUG",
            "propagate": False,
        },
        "datatracker": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "purple": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "rpc": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}
