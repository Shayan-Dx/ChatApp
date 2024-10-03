from Users.authentication import JWTAuthentication
from Users.authentication import get_user_from_payload
from rest_framework.exceptions import AuthenticationFailed
from channels.db import database_sync_to_async

class JWTAuthMiddleware:
    """Custom middleware to authenticate users based on JWT for WebSocket connections."""

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Attempt to authenticate the user
        try:
            user = await database_sync_to_async(self.authenticate_user)(scope)
            scope['user'] = user
        except AuthenticationFailed:
            return await self.close_connection(send)

        # Continue to the inner application with the authenticated user
        return await self.inner(scope, receive, send)

    def authenticate_user(self, scope):
        # Extract and validate the JWT token from the scope headers
        jwt_auth = JWTAuthentication()
        token = self.get_token_from_headers(scope)

        payload = jwt_auth.decode_jwt(token)
        user = get_user_from_payload(payload)
        if user is None:
            raise AuthenticationFailed('User not found')

        return user

    def get_token_from_headers(self, scope):
        headers = dict(scope['headers'])
        if b'authorization' not in headers:
            raise AuthenticationFailed('No authorization header provided')

        auth_header = headers[b'authorization'].decode()
        if not auth_header.startswith('Bearer '):
            raise AuthenticationFailed('Invalid authorization header format')

        return auth_header.split(' ')[1]

    async def close_connection(self, send):
        await send({
            'type': 'websocket.close',
            'code': 4001
        })
