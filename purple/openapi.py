from drf_spectacular.openapi import AutoSchema


class RpcAutoSchema(AutoSchema):
    # pass
    def get_tags(self):
        # Override the default so that we get a single API tag
        return ["purple"]


def exclude_analytics(endpoints, **kwargs):
    """Leave the analytics API out of the purple schema; it has its own"""
    return [e for e in endpoints if not e[0].startswith("/api/analytics/")]
