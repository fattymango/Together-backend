from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def get_user(headers):
    try:
        token_name, token_key = headers[b'authorization'].decode().split()
        if token_name == 'Token':
            token = Token.objects.get(key=token_key)
            return token.user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleWare:
    def __init__(self, app):
        self.app = app
        

    async def __call__(self,scope, receive, send):
        
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            scope['user'] = await get_user(headers)
        else:
            scope['user'] = AnonymousUser()
        return await self.app(scope, receive, send)
    
