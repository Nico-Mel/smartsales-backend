# users/urls.py
from django.urls import path, include
from .auth_views import LoginView, RefreshView, LogoutView
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet, ModuleViewSet, PermissionViewSet
from .admin_views import (
    seed_database_view, 
    reset_database_view,
    seed_sample_data_view,
    reset_sample_data_view
)
router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('roles', RoleViewSet, basename='role')
router.register('modules', ModuleViewSet, basename='module')
router.register('permissions', PermissionViewSet, basename='permission')

urlpatterns = [
    # Bloque de autenticación JWT (puede ser usado tanto por web como por móvil)
    path('auth/login/', LoginView.as_view(), name='jwt_login'),
    path('auth/refresh/', RefreshView.as_view(), name='jwt_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='jwt_logout'),
    path('admin/seeder/seed/', seed_database_view, name='admin_seed'),
    path('admin/seeder/reset/', reset_database_view, name='admin_reset'),
    path('admin/seeder/seed-sample/', seed_sample_data_view, name='admin_seed_sample'),
    path('admin/seeder/reset-sample/', reset_sample_data_view, name='admin_reset_sample'),
    # Bloque de CRUDs (roles, módulos, permisos, usuarios)
    path('', include(router.urls)),
]