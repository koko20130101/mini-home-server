
# from django.contrib import admin
from django.urls import re_path

from apps.AI.consumers import AIConsumer

'''异步： websocket 路由配置 '''
websocket_urlpatterns = [
    re_path(r'ws/ai/$', AIConsumer.as_asgi()),
]
