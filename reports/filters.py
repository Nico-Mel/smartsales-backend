# reports/filters.py

from django_filters import rest_framework as filters
from ventas.models import Venta, Pago

class ReporteVentaFilter(filters.FilterSet):
    """
    Define los filtros de fecha que podemos usar en la URL.
    """
    
    # Crea un filtro para 'fecha >= valor'
    fecha_inicio = filters.DateFilter(
        field_name="fecha", 
        lookup_expr='gte' # Mayor o igual que
    )
    
    # Crea un filtro para 'fecha <= valor'
    fecha_fin = filters.DateFilter(
        field_name="fecha", 
        lookup_expr='lte' # Menor o igual que
    )

    class Meta:
        model = Venta
        # Lista los campos que el filtro manejará
        fields = ['fecha_inicio', 'fecha_fin']

class ReportePagoFilter(filters.FilterSet):
    """
    Define los filtros de fecha para el modelo Pago.
    """
    fecha_inicio = filters.DateFilter(
        field_name="fecha", 
        lookup_expr='gte' 
    )
    fecha_fin = filters.DateFilter(
        field_name="fecha", 
        lookup_expr='lte' 
    )

    class Meta:
        model = Pago # ¡Importante! Este filtro es para el modelo Pago
        fields = ['fecha_inicio', 'fecha_fin']