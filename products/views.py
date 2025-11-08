# products/views.py
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Marca,
    Categoria,
    SubCategoria,
    Producto,
    DetalleProducto,
    ImagenProducto,
    Descuento,
    Campania,
)
from .serializers import (
    MarcaSerializer,
    CategoriaSerializer,
    SubCategoriaSerializer, 
    ProductoSerializer,
    DetalleProductoSerializer,
    ImagenProductoSerializer,
    DescuentoSerializer,
    CampaniaSerializer,
)
from utils.permissions import ModulePermission
from utils.viewsets import SoftDeleteViewSet

class MarcaViewSet(SoftDeleteViewSet):
    queryset = Marca.objects.all().order_by('nombre')
    serializer_class = MarcaSerializer
    module_name = "Marca"

class CategoriaViewSet(SoftDeleteViewSet):
    queryset = Categoria.objects.all().order_by('nombre')
    serializer_class = CategoriaSerializer
    module_name = "Categoria"

class SubCategoriaViewSet(SoftDeleteViewSet): 
    queryset = SubCategoria.objects.all().order_by('categoria__nombre', 'nombre')
    serializer_class = SubCategoriaSerializer
    module_name = "SubCategoria"

class ProductoViewSet(SoftDeleteViewSet):
    queryset = Producto.objects.all().order_by('nombre')
    serializer_class = ProductoSerializer
    module_name = "Producto"

class DetalleProductoViewSet(SoftDeleteViewSet):
    queryset = DetalleProducto.objects.all()
    serializer_class = DetalleProductoSerializer
    module_name = "DetalleProducto"

class ImagenProductoViewSet(SoftDeleteViewSet): 
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
    