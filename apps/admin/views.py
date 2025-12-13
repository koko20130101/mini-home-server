from rest_framework import viewsets, permissions, status, exceptions
from datetime import datetime
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.users.serializers import AdminUsersSerializer, AdminAccountSerializer
from apps.users.models import Users, Account
from apps.assets.models import SystemConfig, GlobalClassify, UploadImages
from apps.assets.serializers import SystemConfigSerializer, AdminGlobalClassifySerializer, UploadImagesSerializer
from apps.AI.models import Agent, Topic, Dialog, AIModels, VoiceRole, DefyAgent, Assess, UserDefy
from apps.AI.serializers import TopicSerializer, AgentAdminSerializer, DialogSerializer, AIModelsAdminSerializer, VoiceRoleAdminSerializer, DefyAgentAdminSerializer, AssessAdminSerializer, UserDefyAdminSerializer
from apps.products.models import Products
from apps.products.serializers import ProductsSerializer
from apps.activity.models import Activity
from apps.activity.serializers import ActivitySerializer
from apps.orders.models import Orders
from apps.orders.serializers import OrdersSerializer
from common.permissions import IsSuperUser
# django自带的验证机制
from django.contrib.auth import authenticate, login, logout  # 验证、登入、登出
from django.core.cache import cache
from common.utils import generate_product_id


class AdminUsersViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = AdminUsersSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    # 指定可以过滤字段
    filterset_fields = ['real_name', 'nick_name', 'created']

    def create(self, request, *args, **kwargs):
        # 不能创建
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def update(self, request, *args, **kwargs):
        # 不能put更新
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    # 登录
    @action(methods=['POST'], detail=False, permission_classes=[])
    def login(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({
                'status': status.HTTP_503_SERVICE_UNAVAILABLE,
                'msg': '用户名或密码不能为空',
            })
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            serializer = self.get_serializer(user)
            return Response({
                'status': status.HTTP_200_OK,
                'msg': '登录成功',
                'data': dict(serializer.data, **{'userName': username})
            })
        else:
            return Response({
                'status': status.HTTP_503_SERVICE_UNAVAILABLE,
                'msg': '用户不存在或用户密码输入错误!!',
            })

    # 登出
    @action(methods=['GET'], detail=False, permission_classes=[])
    def logout(self, request, *args, **kwargs):
        try:
            logout(request)
            return Response({
                'status': status.HTTP_200_OK,
                'msg': '登出成功',
            })
        except:
            return Response({
                'status': status.HTTP_503_SERVICE_UNAVAILABLE,
                'msg': '服务调用失败',
            })

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated, IsSuperUser])
    def setActive(self, request, *args, **kwargs):
        # 设置热门
        id = request.data.get('id')
        is_active = request.data.get('is_active')
        instance = self.filter_queryset(
            self.get_queryset()).filter(id=id).first()
        if instance and instance.is_superuser != 1:
            instance.is_active = is_active
            instance.save()
            return Response({'msg': 'ok'}, status.HTTP_200_OK)
        else:
            return Response({'msg': '无权操作'},
                            status.HTTP_403_FORBIDDEN)


class AdminAccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AdminAccountSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    # 指定可以过滤字段
    filterset_fields = ['vip_type',]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        for item in queryset:
            if item.vip_date and item.vip_date.timestamp() < datetime.now().timestamp() and item.vip_type != 0:
                # 会员过期
                print('会员过期')
                item.vip_type = 0
                item.save()
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # 不能创建
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def destroy(self, request, *args, **kwargs):
        # 不能删除
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})


class AdminAgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    filterset_fields = ['agent_name', 'classify__code']


class AdminAIModelsViewSet(viewsets.ModelViewSet):
    queryset = AIModels.objects.all()
    serializer_class = AIModelsAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    filterset_fields = ['model_type']


class AdminVoiceRoleViewSet(viewsets.ModelViewSet):
    queryset = VoiceRole.objects.all()
    serializer_class = VoiceRoleAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    filterset_fields = ['voice_type', 'ai_model']


class AdminSystemConfigViewSet(viewsets.ModelViewSet):
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    # filterset_fields = ['']

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def clearCache(self, request, *args, **kwargs):
        # 清除缓存
        key = request.data.get('key')
        if key:
            cache.delete('key')
        else:
            cache.clear()
        return Response({"msg": 'not ok'}, status.HTTP_200_OK)


class AdminProductsViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

    def create(self, request, *args, **kwargs):
        # 创建
        serializer = self.get_serializer(
            data={'id': generate_product_id(), **request.data})
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': '创建成功'}, status.HTTP_200_OK)
        else:
            print(serializer.errors)


class AdminActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    # filterset_fields = ['']


class AdminOrdersViewSet(viewsets.ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    filterset_fields = ['id', 'product_name', 'status']


class AdminClassifyViewSet(viewsets.ModelViewSet):
    queryset = GlobalClassify.objects.all()
    serializer_class = AdminGlobalClassifySerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    # 指定可以过滤字段
    filterset_fields = ['id', 'code']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset()).filter(parent__isnull=True)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AdminDefyAgentViewSet(viewsets.ModelViewSet):
    queryset = DefyAgent.objects.all()
    serializer_class = DefyAgentAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    # 指定可以过滤字段
    # filterset_fields = ['']


class AdminAssessViewSet(viewsets.ModelViewSet):
    queryset = Assess.objects.all()
    serializer_class = AssessAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    # filterset_fields = ['']


class AdminUserDefyViewSet(viewsets.ModelViewSet):
    queryset = UserDefy.objects.all()
    serializer_class = UserDefyAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    # filterset_fields = ['']


class AdminUploadImagesViewSet(viewsets.ModelViewSet):
    queryset = UploadImages.objects.all()
    serializer_class = UploadImagesSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    filterset_fields = ['image_type']
