# reports/urls.py

from django.urls import path
from .views import (
    ReporteVentasPorProducto, 
    ReporteVentasPorSucursal,
    ReporteVentasPorVendedor,
    ReporteIngresosPorMetodoPago,
    GenerarReporteNLPView,
    AnalizarVentasProductoView,
)
urlpatterns = [
    path(
        'filtrado/ventas-por-producto/', 
        ReporteVentasPorProducto.as_view(), 
        name='reporte-filtrado-ventas-producto'
    ),
    path(
        'filtrado/ventas-por-sucursal/', 
        ReporteVentasPorSucursal.as_view(), 
        name='reporte-filtrado-ventas-sucursal'
    ),
    path(
        'filtrado/ventas-por-vendedor/', 
        ReporteVentasPorVendedor.as_view(), 
        name='reporte-filtrado-ventas-vendedor'
    ),
    path(
        'filtrado/ingresos-por-metodo-pago/', 
        ReporteIngresosPorMetodoPago.as_view(), 
        name='reporte-filtrado-metodo-pago'
    ),
    path(
        'generar-con-nlp/', 
        GenerarReporteNLPView.as_view(), 
        name='generar-reporte-nlp'
    ),
    path(
        'analizar/ventas-por-producto/', 
        AnalizarVentasProductoView.as_view(), 
        name='analizar-ventas-producto'
    ),
]