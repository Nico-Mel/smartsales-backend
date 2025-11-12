# products/views.py
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .nlp_parser import parse_natural_query

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
    
class BuscarProductoNLPView(APIView):
    """
    Recibe un prompt de texto, lo interpreta con Gemini (Retail),
    y devuelve una lista de productos que coinciden.
    """
    def post(self, request, *args, **kwargs):
        
        prompt = request.data.get('prompt', '')
        if not prompt:
            return Response({"error": "No se proporcionó un 'prompt' de texto."}, status=400)

        # 1. Llamar al "Intérprete" de Productos (El nuevo)
        parsed_json = parse_natural_query(prompt)
        
        if "error" in parsed_json:
            return Response(parsed_json, status=500)

        # 2. Construir el Filtro (Query)
        queryset = Producto.objects.filter(
            empresa=request.user.empresa,
            esta_activo=True
        )
        
        # --- ¡FILTROS MEJORADOS! ---
        
        # Filtro de Nombre (si existe)
        if parsed_json.get('nombre_producto'):
            queryset = queryset.filter(
                nombre__icontains=parsed_json['nombre_producto']
            )
        
        # Filtro de Marca (si existe)
        if parsed_json.get('marca'):
            queryset = queryset.filter(
                marca__nombre__icontains=parsed_json['marca']
            )
            
        # Filtro de Categoría (¡NUEVO!)
        # Asume que: Producto -> subcategoria -> categoria -> nombre
        if parsed_json.get('categoria'):
            queryset = queryset.filter(
                subcategoria__categoria__nombre__icontains=parsed_json['categoria']
            )
            
        # Filtro de Subcategoría (¡Mejorado!)
        # Asume que: Producto -> subcategoria -> nombre
        if parsed_json.get('subcategoria'):
            queryset = queryset.filter(
                subcategoria__nombre__icontains=parsed_json['subcategoria']
            )
        
        # Filtro de Precio Mínimo
        if parsed_json.get('precio_minimo', 0) > 0:
            queryset = queryset.filter(
                precio_venta__gte=parsed_json['precio_minimo']
            )
            
        # Filtro de Precio Máximo
        if parsed_json.get('precio_maximo', 0) > 0:
            queryset = queryset.filter(
                precio_venta__lte=parsed_json['precio_maximo']
            )
        
        # Filtro de Palabras Clave (en descripción)
        palabras_clave = parsed_json.get('palabras_clave', [])
        if palabras_clave:
            q_objects = Q()
            for palabra in palabras_clave:
                q_objects |= Q(descripcion__icontains=palabra)
            queryset = queryset.filter(q_objects)

        # 3. Serializar y Devolver los Resultados
        productos_encontrados = queryset.distinct()[:50]
        
        # Usamos el Serializer que me pasaste
        serializer = ProductoSerializer(productos_encontrados, many=True)
        return Response(serializer.data)