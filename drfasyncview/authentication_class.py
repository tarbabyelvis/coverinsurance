from rest_framework import HTTP_HEADER_ENCODING, exceptions
from asgiref.sync import sync_to_async
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from drfasyncview import AsyncRequest, AsyncAPIView
from rest_framework.throttling import BaseThrottle
import asyncio

@sync_to_async
def get_token(model, key):
    return model.objects.select_related('user').get(key=key)


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.
    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, str):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth

class AsyncAuthentication(BaseAuthentication):    
    """
    Simple token based authentication.
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:
        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = 'Token'
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token


    """
    A custom token model may be used, but must have the following properties.
    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """

    async def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        auth_creds = await self.authenticate_credentials(token)
        return auth_creds

    async def authenticate_credentials(self, key):
        model = None
        if self.model is not None:
            model = self.model
        else:
            from rest_framework.authtoken.models import Token
            model = Token
        try:
            token = await get_token(model, key)

        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return (token.user, token)

    async def authenticate_header(self, request):
        return self.keyword


class AsyncPermission(BasePermission):
    async def has_permission(self, request: AsyncRequest, view: AsyncAPIView) -> bool:
        await asyncio.sleep(0.01)
        return True


class AsyncThrottle(BaseThrottle):
    async def allow_request(self, request: AsyncRequest, view: AsyncAPIView) -> bool:
        await asyncio.sleep(0.01)
        return True

class AsyncIsAuthenticated(BasePermission):
    async def has_permission(self, request: AsyncRequest, view: AsyncAPIView):
        return bool(request.user and request.user.is_authenticated)