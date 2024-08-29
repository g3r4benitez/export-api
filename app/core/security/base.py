from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security import SecurityScopes

from app.exceptions import authentication_exceptions
from app.core.security.providers import BaseAuth
from app.models.user import UserProfile


class JWTBearer(HTTPBearer):
    def __init__(self, auth_provider: BaseAuth, auto_error: bool = True):
        self.__auth_provider = auth_provider
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request, scopes_requested: SecurityScopes = None):
        """
        Validate jwt and scopes
        :param request:
        :param scopes_requested:
        :return:
        """
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials or not credentials.scheme == "Bearer":
            raise authentication_exceptions.UnauthorizedException()
        decoded = self.verify_jwt(credentials.credentials)
        if not self.__auth_provider.require_scopes(scopes_requested, decoded):
            raise authentication_exceptions.ForbiddenException()
        return credentials.credentials

    def verify_jwt(self, jwt_token: str) -> dict:
        """ return decoded token if it's valid"""
        try:
            return self.__auth_provider.jwt_decode_token(jwt_token)
        except Exception as jwt_decode_token_error:
            raise authentication_exceptions.UnauthorizedException() from jwt_decode_token_error


class AuthUser(HTTPBearer):
    def __init__(self, auth_provider: BaseAuth, auto_error: bool = True):
        self.__auth_provider = auth_provider
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> UserProfile:
        """
        Get jwt from headers
        :param request:
        :return:
        """
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        return self.__get_user_profile(credentials.credentials)

    def __get_user_profile(self, jwt_token: str) -> UserProfile:
        user_profile = self.__auth_provider.user_profile(jwt_token)
        return UserProfile(**user_profile)
