"""battleServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from apps.users.views import user, account,fans
from apps.assets.views import ImageUploadViewSet, SystemConfigViewSet, GlobalClassifyViewSet
from apps.AI.views import AgentViewSet, TopicViewSet, DialogViewSet, DefyAgentViewSet, UserDefyViewSet, DefyDialogViewSet
from apps.products.views import ProductsViewSet
from apps.admin import views as views_admin

router = DefaultRouter(trailing_slash=False)

'''接口路由配置'''
# 用户
router.register(r'users', user.UsersViewSet)
router.register(r'account', account.AccountViewSet)
router.register(r'fans', fans.FansViewSet)
# 资源、全局
router.register(r'upload', ImageUploadViewSet)
router.register(r'config', SystemConfigViewSet)
router.register(r'classify', GlobalClassifyViewSet)
# AI
router.register(r'agent', AgentViewSet)
router.register(r'topic', TopicViewSet)
router.register(r'dialog', DialogViewSet)
# AI练习
router.register(r'ai-defy', DefyAgentViewSet)
router.register(r'user-defy', UserDefyViewSet)
router.register(r'defy-dialog', DefyDialogViewSet)
# 商品
router.register(r'products', ProductsViewSet)

'''后台管理路由'''
router.register(r'admin.users', views_admin.AdminUsersViewSet,
                basename='admin-users')
router.register(r'admin.account', views_admin.AdminAccountViewSet,
                basename='admin-account')
router.register(r'admin.agent', views_admin.AdminAgentViewSet,
                basename='admin-agents')
router.register(r'admin.models', views_admin.AdminAIModelsViewSet,
                basename='admin-models')
router.register(r'admin.voice-role', views_admin.AdminVoiceRoleViewSet,
                basename='admin-voice-role')
router.register(r'admin.config', views_admin.AdminSystemConfigViewSet,
                basename='admin-system-config')
router.register(r'admin.images', views_admin.AdminUploadImagesViewSet,
                basename='admin-images')
router.register(r'admin.classify', views_admin.AdminClassifyViewSet,
                basename='admin-classify')
router.register(r'admin.products', views_admin.AdminProductsViewSet,
                basename='admin-products')
router.register(r'admin.activity', views_admin.AdminActivityViewSet,
                basename='admin-activity')
router.register(r'admin.defy', views_admin.AdminDefyAgentViewSet,
                basename='admin-defy')
router.register(r'admin.defyAssess', views_admin.AdminAssessViewSet,
                basename='admin-defy-assess')
router.register(r'admin.defyRecord', views_admin.AdminUserDefyViewSet,
                basename='admin-defy-record')


urlpatterns = [
    path('', include(router.urls)),
    # path('admin/', admin.site.urls),
]

urlpatterns += [
    # path('api-auth/', include('rest_framework.urls')),
]
