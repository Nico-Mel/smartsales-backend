# apps/users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet, ModuleViewSet, PermissionViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('roles', RoleViewSet, basename='role')
router.register('modules', ModuleViewSet, basename='module')
router.register('permissions', PermissionViewSet, basename='permission')

urlpatterns = [
    path('', include(router.urls)),
]
