# sucursales/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartamentoViewSet,
    DireccionViewSet,
    SucursalViewSet,
    StockSucursalViewSet,
)

router = DefaultRouter()
router.register(r"departamentos", DepartamentoViewSet)
router.register(r"direcciones", DireccionViewSet)
router.register(r"sucursales", SucursalViewSet)
router.register(r"stocksucursales", StockSucursalViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
