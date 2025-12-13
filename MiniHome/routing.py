from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from common.auth_ws import TokenAuthMiddleware
import MiniHome.urls_ws


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # 通过TokenAuthMiddleware中间件进行身份验证
    "websocket": TokenAuthMiddleware(
        URLRouter(
            MiniHome.urls_ws.websocket_urlpatterns
        )
    ),
})
