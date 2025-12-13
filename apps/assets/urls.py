from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageUploadViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'upload', ImageUploadViewSet)
urlpatterns = [path('', include(router.urls))]
