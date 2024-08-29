from os import path
from abc import ABC, abstractmethod

import json
import jwt
import requests
from fastapi.security import SecurityScopes
import cognitojwt

from app.exceptions import authentication_exceptions


class BaseAuth(ABC):
    PERMISSION_GROUPS = {'ADMIN': 'admin', 'STAFF': 'staff', 'MEMBER': 'member'}
    USERINFO_PATH = '/userinfo'

    @abstractmethod
    def jwt_decode_token(self, token) -> dict:
        pass

    @classmethod
    @abstractmethod
    def require_scopes(cls, required_scopes: SecurityScopes, jwt_decoded: dict) -> bool:
        pass

    @abstractmethod
    def user_profile(self, token: str) -> dict:
        pass

    @staticmethod
    def get_sub_from_jwt(token: str):
        try:
            token = token.replace("Bearer ", "")
            return jwt.decode(token, options={"verify_signature": False}, algorithms=['RS256'])['sub']
        except Exception as e:
            raise e


class CognitoAuth(BaseAuth):
    def __init__(self, domain: str, region: str, user_pool_id: str, app_client_id: str = ""):
        self.__domain = domain
        self.__region = region
        self.__user_pool_id = user_pool_id
        self.__app_client_id = app_client_id

    def jwt_decode_token(self, token) -> dict:
        try:
            return self.__verify_token(token)
        except Exception as e:
            raise authentication_exceptions.UnauthorizedException() from e

    def __verify_token(self, token: str) -> dict:
        verified_claims: dict = cognitojwt.decode(
            token,
            self.__region,
            self.__user_pool_id,
            app_client_id=self.__app_client_id,  # Optional
            testmode=False  # Disable token expiration check for testing purposes
        )
        return verified_claims

    @staticmethod
    def get_token_auth_header(request) -> str:
        """Obtains the Access Token from the Authorization Header."""
        auth = request.META.get("HTTP_AUTHORIZATION", None)
        parts = auth.split()
        token = parts[1]

        return token

    @classmethod
    def require_scopes(cls, required_scopes: SecurityScopes, jwt_decoded: dict) -> bool:
        """Determines if the required scope is present in the Access Token."""
        if not required_scopes.scopes:
            return True
        if jwt_decoded.get("cognito:groups"):
            user_groups = jwt_decoded["cognito:groups"]
            if cls.PERMISSION_GROUPS['ADMIN'] in user_groups:
                return True
            if set(user_groups) & set(required_scopes.scopes):
                return True
        return False

    def user_profile(self, token: str) -> dict:
        pass


class Auth0Auth(BaseAuth):
    def __init__(self, domain: str, client_id: str, client_secret: str, audience: str, issuer: str):
        self.__domain = domain
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__audience = audience
        self.__issuer = issuer

    def jwt_decode_token(self, token):
        auth0_domain = self.__issuer
        header = jwt.get_unverified_header(token)
        jwks = requests.get(
            path.join(auth0_domain, '.well-known/jwks.json')
        ).json()
        public_key = None
        for jwk in jwks['keys']:
            if jwk['kid'] == header['kid']:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

        if public_key is None:
            raise authentication_exceptions.UnauthorizedException()

        jwt_decoded = jwt.decode(
            token, public_key,
            audience=self.__audience,
            issuer=self.__issuer,
            algorithms=['RS256']
        )

        return jwt_decoded

    def require_scopes(self, required_scopes: SecurityScopes, jwt_decoded: dict) -> bool:
        return True

    def user_profile(self, token: str) -> dict:
        """Return user profile data corresponding to the token provided."""
        response = requests.post(f'{self.__domain}{self.USERINFO_PATH}',
                                 headers={'Authorization': f'Bearer {token}'}).json()
        response["metadata"] = response.pop("https://ceg/user_metadata")
        return response
