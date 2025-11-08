from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartamentoViewSet,
    DireccionViewSet,
    SucursalViewSet,
    StockSucursalViewSet
)

router = DefaultRouter()

# Registramos las rutas
router.register(r'departamentos', DepartamentoViewSet)
router.register(r'direcciones', DireccionViewSet)
router.register(r'sucursales', SucursalViewSet)
router.register(r'stock', StockSucursalViewSet)

urlpatterns = [
    path('', include(router.urls)),
]