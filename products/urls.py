# products/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (MarcaViewSet, CategoriaViewSet, ProductoViewSet,
                    ProductoCategoriaViewSet, DetalleProductoViewSet, ImagenProductoViewSet, DescuentoViewSet, CampaniaViewSet)
router = DefaultRouter()
router.register(r'marcas', MarcaViewSet, basename='marca')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'producto-categorias', ProductoCategoriaViewSet, basename='productocategoria')
router.register(r'detalles', DetalleProductoViewSet, basename='detalleproducto')
router.register(r'imagenes', ImagenProductoViewSet, basename='imagenproducto')
router.register(r'descuentos', DescuentoViewSet, basename='descuento')
router.register(r'campanias', CampaniaViewSet, basename='campania')

urlpatterns = [
    path('', include(router.urls)),     
]

