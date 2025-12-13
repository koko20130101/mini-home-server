from urllib.parse import parse_qs
from django.core.cache import cache
from django.contrib.auth.models import AnonymousUser

class TokenAuthMiddleware:
    """ websocket使用的Token认证中间件 """

    def __init__(self,app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # 解析查询参数
        query_params = parse_qs(scope.get("query_string", b"").decode())
        token = query_params.get("token", [None])[0]
        # 合并参数到 scope
        scope.update(query_params)
        # 验证Token: 从缓存中获取用户
        cache_user = cache.get('token_' + token)
        scope['user'] = cache_user if cache_user  else AnonymousUser() 
        return await self.app(scope, receive, send)
    