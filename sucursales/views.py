from rest_framework import viewsets
from utils.viewsets import SoftDeleteViewSet
from utils.permissions import ModulePermission
from .models import Departamento, Direccion, Sucursal, StockSucursal
from .serializers import (
    DepartamentoSerializer,
    DireccionSerializer,
    SucursalSerializer,
    StockSucursalSerializer,
)


class DepartamentoViewSet(SoftDeleteViewSet):
    queryset = Departamento.objects.all().order_by("nombre")
    serializer_class = DepartamentoSerializer
    module_name = "Departamento"


class DireccionViewSet(SoftDeleteViewSet):
    queryset = Direccion.objects.all().order_by("ciudad", "zona")
    serializer_class = DireccionSerializer
    module_name = "Direccion"


class SucursalViewSet(SoftDeleteViewSet):
    queryset = Sucursal.objects.all().order_by("nombre")
    serializer_class = SucursalSerializer
    module_name = "Sucursal"


class StockSucursalViewSet(SoftDeleteViewSet):
    queryset = StockSucursal.objects.all().order_by("sucursal__nombre")
    serializer_class = StockSucursalSerializer
    module_name = "StockSucursal"
