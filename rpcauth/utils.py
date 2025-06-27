# Copyright The IETF Trust 2025, All Rights Reserved
import warnings
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from django.conf import settings


def op_logout_url(request):
    """Construct URI for initiating logout from OIDC provider"""
    end_session_endpoint = getattr(settings, "OIDC_OP_END_SESSION_ENDPOINT", None)
    logout_redirect_url = getattr(settings, "LOGOUT_REDIRECT_URL", "/")
    if end_session_endpoint is None:
        # No END_SESSION_ENDPOINT is configured so we can't initiate an OP logout
        return logout_redirect_url

    # Per the OIDC spec, end_session_endpoint can include a query string of
    # its own, so parse and preserve it and append our parameters to the end.
    # https://openid.net/specs/openid-connect-rpinitiated-1_0.html
    endpoint_parts = urlsplit(end_session_endpoint)

    if settings.DEPLOYMENT_MODE == "production" and endpoint_parts.scheme != "https":
        warnings.warn(
            "OIDC_OP_END_SESSION_ENDPOINT must be an https URI. Not initiating logout from OP.",
            stacklevel=2
        )
        return logout_redirect_url

    query_params = parse_qsl(endpoint_parts.query)
    # make sure the URL did not already contain any of the params we are about to use
    if any(
        name in ["client_id", "post_logout_redirect_url", "id_token_hint"]
        for name, _ in query_params
    ):
        warnings.warn(
            "OIDC_OP_END_SESSION_ENDPOINT has an inappropriate query param. Not initiating logout from OP.",
            stacklevel=2
        )
        return logout_redirect_url

    # Construct the end-session URL
    query_params.append(
        ("post_logout_redirect_uri", request.build_absolute_uri(logout_redirect_url)),
    )
    # hint with the id token if we have it
    id_token = request.session.get("oidc_id_token", None)
    if id_token is not None:
        query_params.append(("id_token_hint", id_token))
    return urlunsplit(endpoint_parts._replace(query=urlencode(query_params)))
