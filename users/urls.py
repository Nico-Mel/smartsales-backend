# users/urls.py
from django.urls import path, include
from .auth_views import LoginView, RefreshView, LogoutView
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet, ModuleViewSet, PermissionViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('roles', RoleViewSet, basename='role')
router.register('modules', ModuleViewSet, basename='module')
router.register('permissions', PermissionViewSet, basename='permission')

# urlpatterns = [
#     path('login/', UserViewSet.as_view({'post': 'login'}), name='login'),
#     path('logout/', UserViewSet.as_view({'post': 'logout'}), name='logout'),
#     path('', include(router.urls)),
# ]
urlpatterns = [
    # Bloque de autenticación JWT (puede ser usado tanto por web como por móvil)
    path('auth/login/', LoginView.as_view(), name='jwt_login'),
    path('auth/refresh/', RefreshView.as_view(), name='jwt_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='jwt_logout'),
    # Bloque de CRUDs (roles, módulos, permisos, usuarios)
    path('', include(router.urls)),
]