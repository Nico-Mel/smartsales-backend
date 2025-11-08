from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
  MisDireccionesViewSet
)

router = DefaultRouter()

# Registramos las rutas
router.register(r'mis-direcciones', MisDireccionesViewSet, basename='mis-direcciones')

urlpatterns = [
    path('', include(router.urls)),
]