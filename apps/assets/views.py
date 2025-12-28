from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import UploadImages, SystemConfig, GlobalClassify
from .serializers import UploadImagesSerializer, SystemConfigSerializer, GlobalClassifySerializer
from apps.AI.models import AIModels
from common.ai_asr import getAliyunToken
from common.ai_tts import getAliyunTTSToken
from django.core.cache import cache
from datetime import datetime


class ImageUploadViewSet(viewsets.ModelViewSet):
    '''上传图片视图集'''
    queryset = UploadImages.objects.all()
    serializer_class = UploadImagesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        # 不能查看列表
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def retrieve(self, request, *args, **kwargs):
        # 不能get查看信息
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


class SystemConfigViewSet(viewsets.ModelViewSet):
    '''系统设置视图集'''
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer

    def list(self, request, *args, **kwargs):
        # 不能查看列表
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def create(self, request, *args, **kwargs):
        # 不能创建
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def retrieve(self, request, *args, **kwargs):
        # 不能get查看信息
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def update(self, request, *args, **kwargs):
        # 不能put更新
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def destroy(self, request, *args, **kwargs):
        # 不能删除
        raise exceptions.AuthenticationFailed(

            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    @action(methods=['GET'], detail=False)
    def switch(self, request, *args, **kwargs):
        instance = self.get_queryset().filter(id=1).first()
        if instance:
            return Response(instance.config_val, status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def aliyuntoken(self, request, *args, **kwargs):
        asr_code = request.data.get('code')
        # 存到缓存中，30天过期
        # cache.set(asr_code, asr, 30*24*60*60)
        if asr_code == 'ali_asr':
            # 阿里云语音识别
            asr = {'token': '', 'app_key': '',
                   'tts_appkey': '', 'tts_token': ''}
            # 当前时间戳
            current_timestamp = int(datetime.now().timestamp())
            ali_asr_list = cache.get(asr_code) if cache.get(asr_code) else []
            # 我的账号
            my_ali_asr = cache.get('ali_asr_koko')

            if not my_ali_asr:
                # 我的账号
                my_ali_asr = AIModels.objects.filter(
                    model_code='ali_asr_koko', is_enabled=True).first()

                if my_ali_asr:
                    tokenInfo = getAliyunToken(
                        my_ali_asr.accesskey_id, my_ali_asr.api_key)
                    my_ali_asr.token = tokenInfo['token']
                    # 存入缓存
                    cache.set('ali_asr_koko', my_ali_asr,
                              tokenInfo['expireTime'] - current_timestamp)

            if len(ali_asr_list) == 0:
                ali_asr_list = list(AIModels.objects.filter(model_code=asr_code, is_enabled=True).values(
                    'id', 'accesskey_id', 'api_key', 'app_key', 'call_count'))
                for asr_item in ali_asr_list:
                    tokenInfo = getAliyunToken(
                        asr_item['accesskey_id'], asr_item['api_key'])
                    asr_item['token'] = tokenInfo['token']
                    asr_item['tts_token'] = ''
                    asr_item['tts_appkey'] = ''
                    asr_item['count'] = 0  # 获取计数
                    asr_item['timestamp'] = current_timestamp  # 最新获取时间戳
                if ali_asr_list:
                    # 存入缓存
                    cache.set(asr_code, ali_asr_list,
                              tokenInfo['expireTime'] - current_timestamp)
                    # 存过期时间戳
                    cache.set('ali_asr_expires', tokenInfo['expireTime'])

            for asr_item in ali_asr_list:
                if asr_item['count'] < asr_item['call_count']:
                    asr = asr_item
                    asr_item['count'] += 1
                    # 更新获取时间戳
                    asr_item['timestamp'] = current_timestamp
                    if asr_item['app_key'] == 'd1bShNkCMDQrvWSm':
                        # 如果是人和智的账号，tts换成我的
                        asr_item['tts_token'] = my_ali_asr.token
                        asr_item['tts_appkey'] = my_ali_asr.app_key
                    break
                if current_timestamp - asr_item['timestamp'] > 5*60:
                    # 5分钟后重新释放
                    asr = asr_item
                    asr_item['count'] = 1
                    # 更新获取时间戳
                    asr_item['timestamp'] = current_timestamp
                    break
            expires_at = cache.get('ali_asr_expires')
            print('重新存入缓存', expires_at)
            if expires_at:
                # 重新存入缓存
                cache.set(asr_code, ali_asr_list, expires_at-current_timestamp)
            if asr['token'] == '' and my_ali_asr:
                # 取我的账号
                asr['token'] = my_ali_asr.token
                asr['app_key'] = my_ali_asr.app_key
            print(ali_asr_list)
            return Response({'token': asr['token'], 'appkey': asr['app_key'], 'tts_appkey': asr['tts_appkey'], 'tts_token': asr['tts_token']}, status.HTTP_200_OK)
        else:
            return Response({"msg": '获取失败'}, status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def releaseAliyuntoken(self, request, *args, **kwargs):
        # 释放阿里云token
        token = request.data.get('token')
        asr_code = 'ali_asr'
        if token:
            ali_asr_list = cache.get(asr_code) if cache.get(asr_code) else []
            # 当前时间戳
            current_timestamp = int(datetime.now().timestamp())
            for asr_item in ali_asr_list:
                if asr_item['token'] == token:
                    asr_item['count'] -= 1
                    break
            expires_at = cache.get('ali_asr_expires')
            if expires_at:
                # 重新存入缓存
                cache.set(asr_code, ali_asr_list, expires_at-current_timestamp)
            return Response({"msg": 'ok'}, status.HTTP_200_OK)
        else:
            return Response({"msg": 'not ok'}, status.HTTP_200_OK)
        
    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def aliyunTTStoken(self, request, *args, **kwargs):
        tts_code = request.data.get('code')
        if tts_code:
            ali_tts = AIModels.objects.filter(
                    model_code=tts_code, is_enabled=True).first()
            print(11,ali_tts)
            if ali_tts:
                    token = getAliyunTTSToken(ali_tts.api_key)
            return Response({'token': token}, status.HTTP_200_OK)
        else:
            return Response({"msg": '获取失败'}, status.HTTP_503_SERVICE_UNAVAILABLE)


class GlobalClassifyViewSet(viewsets.ModelViewSet):
    '''分类视图集'''
    queryset = GlobalClassify.objects.all()
    serializer_class = GlobalClassifySerializer
    filterset_fields = ['code']

    def create(self, request, *args, **kwargs):
        # 不能创建
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def retrieve(self, request, *args, **kwargs):
        # 不能get查看信息
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def update(self, request, *args, **kwargs):
        # 不能put更新
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def destroy(self, request, *args, **kwargs):
        # 不能删除
        raise exceptions.AuthenticationFailed(

            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})
