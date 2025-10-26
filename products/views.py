# products/views.py
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Marca, Categoria, Producto, ProductoCategoria, DetalleProducto, ImagenProducto, Descuento, Campania
from .serializers import (MarcaSerializer, CategoriaSerializer, ProductoSerializer,
                          ProductoCategoriaSerializer, DetalleProductoSerializer, ImagenProductoSerializer, DescuentoSerializer, CampaniaSerializer)
from utils.permissions import ModulePermission

# Create your views here.
class SoftDeleteViewSet(viewsets.ModelViewSet):
    """
    Clase base reutilizable que agrega:
    - acciones para activar/desactivar (soft delete) registros.
    -Integración con permisos por módulo y acción.
    """
    permission_classes = [ModulePermission]

    def get_queryset(self):
        """
        Si deseas filtrar solo los activos, descomenta:
        return self.queryset.filter(esta_activo=True)
        """
        return self.queryset
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        obj = self.get_object()
        obj.esta_activo = False
        obj.save()
        return Response({'detail': 'Desactivado correctamente.'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        obj = self.get_object()
        obj.esta_activo = True
        obj.save()
        return Response({'detail': 'Activado correctamente.'}, status=status.HTTP_200_OK)

class MarcaViewSet(SoftDeleteViewSet):
    queryset = Marca.objects.all().order_by('nombre')
    serializer_class = MarcaSerializer
    module_name = "Marca"

class CategoriaViewSet(SoftDeleteViewSet):
    queryset = Categoria.objects.all().order_by('nombre')
    serializer_class = CategoriaSerializer
    module_name = "Categoria"

class ProductoViewSet(SoftDeleteViewSet):
    queryset = Producto.objects.all().order_by('nombre')
    serializer_class = ProductoSerializer
    module_name = "Producto"

class ProductoCategoriaViewSet(viewsets.ModelViewSet):
    queryset = ProductoCategoria.objects.all()
    serializer_class = ProductoCategoriaSerializer
    module_name = "ProductoCategoria"

class DetalleProductoViewSet(SoftDeleteViewSet):
    queryset = DetalleProducto.objects.all()
    serializer_class = DetalleProductoSerializer
    module_name = "DetalleProducto"

class ImagenProductoViewSet(viewsets.ModelViewSet):
    queryset = ImagenProducto.objects.all()
    serializer_class = ImagenProductoSerializer
    module_name = "ImagenProducto"

class CampaniaViewSet(SoftDeleteViewSet):
    queryset = Campania.objects.all()
    serializer_class = CampaniaSerializer
    module_name = "Campania"

class DescuentoViewSet(SoftDeleteViewSet):
    queryset = Descuento.objects.all()
    serializer_class = DescuentoSerializer
    module_name = "Descuento"
    