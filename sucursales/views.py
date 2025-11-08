from django.shortcuts import render
#no importar nada de shipping para evitar dependencias circulares

# Create your views here.
from rest_framework import viewsets
from .models import Departamento, Direccion, Sucursal, StockSucursal
from .serializers import (
    DepartamentoSerializer, 
    DireccionSerializer, 
    SucursalSerializer, 
    StockSucursalSerializer
)
from utils.viewsets import SoftDeleteViewSet 
class DepartamentoViewSet(viewsets.ModelViewSet):
    queryset = Departamento.objects.all().order_by('nombre')
    serializer_class = DepartamentoSerializer

class DireccionViewSet(viewsets.ModelViewSet):
    queryset = Direccion.objects.all()
    serializer_class = DireccionSerializer

class SucursalViewSet(SoftDeleteViewSet):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer
    module_name = "Sucursal" 

    def get_queryset(self):
        return Sucursal.objects.select_related(
            'direccion', 
            'direccion__departamento'
        ).all()

class StockSucursalViewSet(viewsets.ModelViewSet):
    queryset = StockSucursal.objects.all()
    serializer_class = StockSucursalSerializer
    module_name = "Stock" 
    
    def get_queryset(self):

        return StockSucursal.objects.select_related(
            'producto', 
            'sucursal'
        ).all()