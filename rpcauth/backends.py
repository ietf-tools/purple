# Copyright The IETF Trust 2023, All Rights Reserved

import datetime
from urllib.parse import urlparse

import requests
from django.core.exceptions import SuspiciousOperation
from django.db import IntegrityError
from django.utils.encoding import smart_str
from josepy.jws import JWS, Header
from mozilla_django_oidc.auth import OIDCAuthenticationBackend, import_from_settings
from requests.auth import HTTPBasicAuth


class ServiceTokenOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    """OIDCAuthenticationBackend that adds Cloudflare service token headers"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.CF_SERVICE_TOKEN_HOSTS = self.get_settings("CF_SERVICE_TOKEN_HOSTS", [])
        self.CF_SERVICE_TOKEN_ID = self.get_settings("CF_SERVICE_TOKEN_ID", None)
        self.CF_SERVICE_TOKEN_SECRET = self.get_settings(
            "CF_SERVICE_TOKEN_SECRET", None
        )

    def _request_get(self, url, *args, **kwargs):
        if urlparse(url).hostname in self.CF_SERVICE_TOKEN_HOSTS:
            if (
                self.CF_SERVICE_TOKEN_ID is not None
                and self.CF_SERVICE_TOKEN_SECRET is not None
            ):
                extra_headers = {
                    "CF-Access-Client-Id": self.CF_SERVICE_TOKEN_ID,
                    "CF-Access-Client-Secret": self.CF_SERVICE_TOKEN_SECRET,
                }
                kwargs["headers"] = kwargs.get("headers", {}) | extra_headers
        return requests.get(url, *args, **kwargs)

    def _request_post(self, url, *args, **kwargs):
        if urlparse(url).hostname in self.CF_SERVICE_TOKEN_HOSTS:
            if (
                self.CF_SERVICE_TOKEN_ID is not None
                and self.CF_SERVICE_TOKEN_SECRET is not None
            ):
                extra_headers = {
                    "CF-Access-Client-Id": self.CF_SERVICE_TOKEN_ID,
                    "CF-Access-Client-Secret": self.CF_SERVICE_TOKEN_SECRET,
                }
                kwargs["headers"] = kwargs.get("headers", {}) | extra_headers
        return requests.post(url, *args, **kwargs)

    def retrieve_matching_jwk(self, token):
        """Get the signing key by exploring the JWKS endpoint of the OP."""
        response_jwks = self._request_get(
            self.OIDC_OP_JWKS_ENDPOINT,
            verify=self.get_settings("OIDC_VERIFY_SSL", True),
            timeout=self.get_settings("OIDC_TIMEOUT", None),
            proxies=self.get_settings("OIDC_PROXY", None),
        )
        response_jwks.raise_for_status()
        jwks = response_jwks.json()

        # Compute the current header from the given token to find a match
        jws = JWS.from_compact(token)
        json_header = jws.signature.protected
        header = Header.json_loads(json_header)

        key = None
        for jwk in jwks["keys"]:
            if import_from_settings("OIDC_VERIFY_KID", True) and jwk[
                "kid"
            ] != smart_str(header.kid):
                continue
            if "alg" in jwk and jwk["alg"] != smart_str(header.alg):
                continue
            key = jwk
        if key is None:
            raise SuspiciousOperation("Could not find a valid JWKS.")
        return key

    def get_token(self, payload):
        """Return token object as a dictionary."""

        auth = None
        if self.get_settings("OIDC_TOKEN_USE_BASIC_AUTH", False):
            # When Basic auth is defined, create the Auth Header and remove secret from payload.
            user = payload.get("client_id")
            pw = payload.get("client_secret")

            auth = HTTPBasicAuth(user, pw)
            del payload["client_secret"]

        response = self._request_post(
            self.OIDC_OP_TOKEN_ENDPOINT,
            data=payload,
            auth=auth,
            verify=self.get_settings("OIDC_VERIFY_SSL", True),
            timeout=self.get_settings("OIDC_TIMEOUT", None),
            proxies=self.get_settings("OIDC_PROXY", None),
        )
        self.raise_token_response_error(response)
        return response.json()

    def get_userinfo(self, access_token, id_token, payload):
        """Return user details dictionary. The id_token and payload are not used in
        the default implementation, but may be used when overriding this method"""

        user_response = self._request_get(
            self.OIDC_OP_USER_ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}"},
            verify=self.get_settings("OIDC_VERIFY_SSL", True),
            timeout=self.get_settings("OIDC_TIMEOUT", None),
            proxies=self.get_settings("OIDC_PROXY", None),
        )
        user_response.raise_for_status()
        return user_response.json()


class RpcOIDCAuthBackend(ServiceTokenOIDCAuthenticationBackend):
    """Customized OIDC auth backend

    Assumes the datatracker makes the following claims:
      sub - pk of the Person who was authenticated, as a string
      roles - list of 2-tuples corresponding to Person's active roles
    """

    ADMIN_ACCESS_ROLE = ["leadmaintainer", "tools"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._subject_id = None  # subject ID we are working with
        self.OIDC_OP_ISSUER_ID = self.get_settings("OIDC_OP_ISSUER_ID")

    def create_user(self, claims):
        """Create a User following a successful auth"""
        subject_id = claims["sub"]
        admin_access = self.ADMIN_ACCESS_ROLE in claims["roles"]

        try:
            new_user = self.UserModel.objects.create(
                username=f"dt-subject-{subject_id}",
                datatracker_subject_id=subject_id,
                name=claims["name"],  # required claim,
                avatar=claims.get("picture", ""),
                is_staff=admin_access,
                is_superuser=admin_access,
            )
        except IntegrityError as err:
            # exception message gets logged - user only sees a failed auth
            raise SuspiciousOperation(
                f"User already exists for datatracker user {subject_id}"
            ) from err
        return new_user

    def update_user(self, user, claims):
        """Update a User following auth"""
        updated = False
        if user.name != claims["name"]:  # required claim
            user.name = claims["name"]
            updated = True
        if user.avatar != claims.get("picture", ""):
            user.avatar = claims.get("picture")
            updated = True

        admin_access = self.ADMIN_ACCESS_ROLE in claims["roles"]
        if user.is_staff != admin_access:
            user.is_staff = admin_access
            updated = True
        if user.is_superuser != admin_access:
            user.is_superuser = admin_access
            updated = True

        if updated:
            user.save()
        return user

    def filter_users_by_claims(self, claims):
        """Return list or queryset of users who satisfy claims

        If the set does not have exactly one member, auth will be rejected.
        """
        return self.UserModel.objects.filter(
            datatracker_subject_id=claims["sub"]  # claim guaranteed to exist
        )

    def verify_token(self, token, **kwargs):
        """Verify the ID token"""
        payload = super().verify_token(token, **kwargs)
        # Validation mandated by sect 3.1.3.7 of the spec not performed by base backend class
        issuer_id = payload.get("iss", None)
        if issuer_id is None or issuer_id != self.OIDC_OP_ISSUER_ID:
            raise SuspiciousOperation(
                f'issuer "{issuer_id}" does not match configured issuer "{self.OIDC_OP_ISSUER_ID}"'
            )
        # Check audience. Per spec, we must reject the token if it "does not list the Client as a
        # valid audience, or if it contains additional audiences not trusted by the Client." We only
        # expect one audience from the datatracker, so let's assume any other audiences are untrusted.
        audience = payload.get("aud", [])
        if isinstance(audience, str):
            audience = [audience]
        if len(set(audience)) != 1 or audience[0] != self.OIDC_RP_CLIENT_ID:
            raise SuspiciousOperation(f'token has invalid audience "{audience}"')
        # azp should be present if token contains multiple audiences, but we rejected such a token already.
        # Just check that, if present, azp is us
        if "azp" in payload and payload["azp"] != self.OIDC_RP_CLIENT_ID:
            raise SuspiciousOperation(
                'token azp ("{}") is not our client id ("{}")'.format(
                    payload["azp"], self.OIDC_RP_CLIENT_ID
                )
            )

        if "exp" not in payload:
            raise SuspiciousOperation("token has no expiration time")
        if not isinstance(payload["exp"], int):
            raise SuspiciousOperation(
                'token exp ("{}") is not an integer'.format(payload["exp"])
            )
        expiration_time = datetime.datetime.fromtimestamp(
            payload["exp"], tz=datetime.UTC
        )
        if expiration_time < datetime.datetime.now(tz=datetime.UTC):
            raise SuspiciousOperation(f"token expired at {expiration_time}")

        # remember the subject ID so we can validate claims later
        if "sub" in payload:
            self._subject_id = payload["sub"]
        else:
            raise SuspiciousOperation("No subject ID in token")
        return payload

    def verify_claims(self, claims):
        """Verify that userinfo claims are sufficient to allow auth"""
        # Per https://openid.net/specs/openid-connect-core-1_0.html#UserInfoResponse,
        # client must validate sub in userinfo response or do nothing else with the
        # response.
        if "sub" not in claims:
            raise SuspiciousOperation("No subject ID claim")
        elif claims["sub"] != self._subject_id:
            raise SuspiciousOperation(
                'userinfo sub ("{}") does not match token sub ("{}")'.format(
                    claims["sub"], self._subject_id
                )
            )

        required_claims = {"sub", "name", "roles"}
        if required_claims.intersection(claims.keys()) != required_claims:
            return False

        # Check datatracker roles
        claim_roles = claims["roles"]
        return ["secr", "secretariat"] in claim_roles or ["auth", "rpc"] in claim_roles
