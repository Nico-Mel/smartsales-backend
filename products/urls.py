# products/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MarcaViewSet,
    CategoriaViewSet,
    SubCategoriaViewSet,  
    ProductoViewSet,
    DetalleProductoViewSet,
    ImagenProductoViewSet,
    DescuentoViewSet,
    CampaniaViewSet,
    BuscarProductoNLPView,
)

router = DefaultRouter()
router.register(r'marca', MarcaViewSet)
router.register(r'categoria', CategoriaViewSet)
router.register(r'subcategoria', SubCategoriaViewSet) 
router.register(r'producto', ProductoViewSet)
router.register(r'detalle', DetalleProductoViewSet)
router.register(r'imagenes', ImagenProductoViewSet)
router.register(r'descuentos', DescuentoViewSet)
router.register(r'campanias', CampaniaViewSet)

urlpatterns = [
    path('', include(router.urls)),   
    path(
        'busqueda-inteligente/', 
        BuscarProductoNLPView.as_view(), 
        name='buscar-producto-nlp'
    ), 
]

