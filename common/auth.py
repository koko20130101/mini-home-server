from datetime import datetime, timedelta
# import pytz
# from django.utils.translation import ugettext_lazy
from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import HTTP_HEADER_ENCODING

# 获取请求头信息


def get_authorization_header(request):
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, type('')):
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


class ExpiringTokenAuthentication(BaseAuthentication):
    model = Token

    def authenticate(self, request):

        auth = get_authorization_header(request)
        if not auth:
            return None
        try:
            token = auth.decode()
        except UnicodeError:
            msg = '无效的token，Token头不应包含无效字符'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        token_cache = 'token_' + key
        cache_user = cache.get(token_cache)

        if cache_user:
            return cache_user, cache_user
        try:
            token = self.model.objects.get(key=key)
        except:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '认证失败'})
        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_403_FORBIDDEN, 'msg': '用户被禁用，请联系管理员'})

        if token.created.timestamp() < (datetime.now() - timedelta(days=90)).timestamp():
            raise exceptions.AuthenticationFailed(
                {'status': status.HTTP_401_UNAUTHORIZED, 'msg': '登录过期，请重新登录'})

        if token:
            token_cache = 'token_' + key
            cache.set(token_cache, token.user, 3*24*60*60)  # 缓存时间3天,单位(秒)

        return token.user, token

    def authenticate_header(self, request):
        return 'Token'
