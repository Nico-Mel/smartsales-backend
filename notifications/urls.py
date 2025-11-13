# notifications/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificacionViewSet
from .views import NotificacionTestView

router = DefaultRouter()
router.register(r'notificaciones', NotificacionViewSet, basename='notificacion')

urlpatterns = [
    path('', include(router.urls)),
    path('test-notificacion/', NotificacionTestView.as_view(), name='test-notificacion'),
]
