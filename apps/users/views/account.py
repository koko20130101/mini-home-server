from rest_framework import viewsets, status, permissions, exceptions
from datetime import date, datetime
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.users.serializers import AccountSerializer
from common.permissions import IsOwner
from apps.users.models import Account


class AccountViewSet(viewsets.ModelViewSet):
    '''账户视图集'''
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def list(self, request, *args, **kwargs):
        # 不能查看用户列表
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def create(self, request, *args, **kwargs):
        # 不能创建
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def update(self, request, *args, **kwargs):
        # 不能put更新
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def retrieve(self, request, *args, **kwargs):
        # 不能get查看用户信息
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def destroy(self, request, *args, **kwargs):
        # 不能删除
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    # 账户信息

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def accountInfo(self, request, *args, **kwargs):
        instance = self.filter_queryset(
            self.get_queryset()).filter(user=request.user).first()
        if instance:
            serializer = self.get_serializer(instance)
            if instance.update_date != date.today():
                # 重置账户数据
                instance.ai_count = {0: 3, 1: 60,
                                     2: 80, 3: 100}[instance.vip_type]
                instance.update_date = date.today()
                instance.save()
            if instance.vip_date and instance.vip_date.timestamp() < datetime.now().timestamp() and instance.vip_type != 0:
                # 会员过期
                instance.vip_type = 0
                instance.ai_count = 3
                instance.save()

            return Response(serializer.data, status.HTTP_200_OK)

        else:
            serializer = AccountSerializer(
                data={'happy_coin': 5, 'ai_count': 3, 'user': request.user.id})
            if serializer.is_valid():
                serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
