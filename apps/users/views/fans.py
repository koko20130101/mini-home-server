from rest_framework import viewsets, status, permissions, exceptions
from datetime import date, datetime
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.users.serializers import FansSerializer
from apps.users.models import Fans, Users
# from common.permissions import IsOwner


class FansViewSet(viewsets.ModelViewSet):
    '''账户视图集'''
    queryset = Fans.objects.all()
    serializer_class = FansSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset()).filter(user_id=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

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

    # 粉丝总数

    @action(methods=['GET'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def fansTotal(self, request, *args, **kwargs):
        instance = self.filter_queryset(
            self.get_queryset()).filter(user=request.user)

        return Response(len(instance), status.HTTP_200_OK)

    # 绑定粉丝

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def bindingFans(self, request, *args, **kwargs):
        inviteId = request.data.get('inviteId')
        user = request.user

        if user and inviteId:
            try:
                # 邀请人
                invite = Users.objects.filter(id=inviteId).first()
                if invite and invite.id != user.id:
                    # 新增
                    fansSerializer = FansSerializer(
                        data={'user': invite.id, 'fans': user.id})
                    if fansSerializer.is_valid():
                        fansSerializer.save()
                        return Response({'msg': '操作成功'}, status.HTTP_200_OK)
            except:
                pass
        return Response({'msg': 'not ok'}, status.HTTP_200_OK)
