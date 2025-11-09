# shipping/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AgenciaViewSet, EnvioViewSet, MisDireccionesViewSet

router = DefaultRouter()
router.register(r"agencias", AgenciaViewSet)
router.register(r"envios", EnvioViewSet)
router.register(r"mis-direcciones", MisDireccionesViewSet, basename="mis-direcciones")

urlpatterns = [
    path("", include(router.urls)),
]
