# users/urls.py
from django.urls import path, include
from .auth_views import LoginView, RefreshView, LogoutView, UserProfileView, RegisterView
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet, ModuleViewSet, PermissionViewSet, ChangePasswordView
from .admin_views import (
    seed_database_view,
    seed_sample_data_view,
    reset_all_data_view,
    seed_products_data_view,
    seed_sales_data_view,
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
    path('auth/register/', RegisterView.as_view(), name='user_register'),
    path('auth/me/', UserProfileView.as_view(), name='user_profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='auth_change_password'), 

    path('admin/seeder/seed-users/', seed_database_view, name='admin_seed_users'),
    path('admin/seeder/seed-sample/', seed_sample_data_view, name='admin_seed_sample'),  
    path('admin/seeder/seed-products/', seed_products_data_view, name='admin_seed_products'),    
    path('admin/seeder/seed-sales/', seed_sales_data_view, name='admin_seed_sales'), 
    path('admin/seeder/reset-all/', reset_all_data_view, name='admin_reset_all'),


    # Bloque de CRUDs (roles, módulos, permisos, usuarios)
    path('', include(router.urls)),
]