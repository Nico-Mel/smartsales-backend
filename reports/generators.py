# reports/generators.py
# ¡Aquí es donde vive la lógica pesada!

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Sum, Count
from django.utils import timezone
from io import BytesIO
import pandas as pd
from weasyprint import HTML

from ventas.models import DetalleVenta, Venta, Pago

# --- FUNCIÓN 1: REPORTE DE PRODUCTO ---
def generar_reporte_producto(request, formato, fecha_inicio, fecha_fin):
    
    # Preparamos las fechas para el nombre del archivo
    fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
    fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')

    # 1. Consulta Base
    base_query = Venta.objects.filter(
        estado='Completado',
        empresa=request.user.empresa
    )
    ventas_filtradas = base_query.filter(
        fecha__range=[fecha_inicio, fecha_fin]
    )
    
    if not ventas_filtradas.exists():
        return HttpResponse("No se encontraron ventas para este rango.", status=404)

    # 2. Consulta Específica del Reporte
    ventas_ids = ventas_filtradas.values_list('id', flat=True)
    datos_reporte = DetalleVenta.objects.filter(
        venta__id__in=ventas_ids
    ).values(
        'producto__nombre', 'producto__sku'
    ).annotate(
        cantidad_total=Sum('cantidad'),
        ingresos_totales=Sum('subtotal')
    ).order_by('-ingresos_totales')

    if not datos_reporte:
        return HttpResponse("Sin datos de detalle de venta.", status=404)
        
    filename_base = f"reporte_producto_DESDE_{fecha_inicio_str}_HASTA_{fecha_fin_str}"

    # 3. Generación de Archivo
    if formato == 'pdf':
        total_general = datos_reporte.aggregate(
            total_cantidad=Sum('cantidad_total'),
            total_ingresos=Sum('ingresos_totales')
        )
        context = {
            'datos': datos_reporte, 'total_general': total_general,
            'fecha_inicio_str': fecha_inicio_str, 'fecha_fin_str': fecha_fin_str,
        }
        html_string = render_to_string('reports/ventas_por_producto.html', context)
        pdf_file = HTML(string=html_string).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename_base}.pdf"'
        return response

    elif formato == 'excel' or formato == 'csv':
        df = pd.DataFrame(list(datos_reporte))
        df.rename(columns={
            'producto__nombre': 'Producto', 'producto__sku': 'SKU',
            'cantidad_total': 'Cantidad Vendida', 'ingresos_totales': 'Ingresos Totales (Bs.)'
        }, inplace=True)
        
        if formato == 'excel':
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Ventas_por_Producto', index=False)
            output.seek(0)
            response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename_base}.xlsx"'
            return response
        
        elif formato == 'csv':
            csv_data = df.to_csv(index=False, encoding='utf-8')
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename_base}.csv"'
            return response
            
    return HttpResponse(f"Formato '{formato}' no soportado.", status=400)


# --- FUNCIÓN 2: REPORTE DE SUCURSAL ---
def generar_reporte_sucursal(request, formato, fecha_inicio, fecha_fin):
    
    fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
    fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')

    # 1. Consulta Base
    base_query = Venta.objects.filter(
        estado='Completado',
        empresa=request.user.empresa
    )
    ventas_filtradas = base_query.filter(
        fecha__range=[fecha_inicio, fecha_fin]
    )
    
    if not ventas_filtradas.exists():
        return HttpResponse("No se encontraron ventas para este rango.", status=404)

    # 2. Consulta Específica del Reporte
    datos_reporte = ventas_filtradas.values(
        'sucursal__nombre'
    ).annotate(
        numero_ventas=Count('id'),
        ingresos_totales=Sum('total')
    ).order_by('-ingresos_totales')

    if not datos_reporte:
        return HttpResponse("Sin datos para el reporte.", status=404)
        
    filename_base = f"reporte_sucursal_DESDE_{fecha_inicio_str}_HASTA_{fecha_fin_str}"

    # 3. Generación de Archivo
    if formato == 'pdf':
        context = {
            'datos_reporte': datos_reporte, # Tu plantilla usa 'datos_reporte' o 'datos'?
            'datos': datos_reporte, # Añadimos ambos por si acaso
            'fecha_inicio_str': fecha_inicio_str, 'fecha_fin_str': fecha_fin_str,
        }
        html_string = render_to_string('reports/ventas_por_sucursal.html', context)
        pdf_file = HTML(string=html_string).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename_base}.pdf"'
        return response

    elif formato == 'excel' or formato == 'csv':
        df = pd.DataFrame(list(datos_reporte))
        df.rename(columns={
            'sucursal__nombre': 'Sucursal',
            'numero_ventas': 'Cantidad de Ventas',
            'ingresos_totales': 'Ingresos Totales (Bs.)'
        }, inplace=True)
        
        if formato == 'excel':
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Ventas_por_Sucursal', index=False)
            output.seek(0)
            response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename_base}.xlsx"'
            return response
        
        elif formato == 'csv':
            csv_data = df.to_csv(index=False, encoding='utf-8')
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename_base}.csv"'
            return response
            
    return HttpResponse(f"Formato '{formato}' no soportado.", status=400)


# --- FUNCIÓN 3: REPORTE DE VENDEDOR ---
def generar_reporte_vendedor(request, formato, fecha_inicio, fecha_fin):
    
    fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
    fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')

    # 1. Consulta Base
    base_query = Venta.objects.filter(
        estado='Completado',
        empresa=request.user.empresa,
        canal='POS' # El filtro clave de este reporte
    )
    ventas_filtradas = base_query.filter(
        fecha__range=[fecha_inicio, fecha_fin]
    )
    
    if not ventas_filtradas.exists():
        return HttpResponse("No se encontraron ventas de VENDEDOR (POS) para este rango.", status=404)

    # 2. Consulta Específica del Reporte
    datos_reporte = ventas_filtradas.values(
        'usuario__email', 'usuario__nombre', 'usuario__apellido',
    ).annotate(
        numero_ventas=Count('id'),
        ingresos_totales=Sum('total')
    ).order_by('-ingresos_totales')

    if not datos_reporte:
        return HttpResponse("Sin datos para el reporte.", status=404)
        
    filename_base = f"reporte_vendedor_DESDE_{fecha_inicio_str}_HASTA_{fecha_fin_str}"

    # 3. Generación de Archivo
    if formato == 'pdf':
        context = {
            'datos_reporte': datos_reporte,
            'fecha_inicio_str': fecha_inicio_str, 'fecha_fin_str': fecha_fin_str,
        }
        html_string = render_to_string('reports/ventas_por_vendedor.html', context)
        pdf_file = HTML(string=html_string).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename_base}.pdf"'
        return response

    elif formato == 'excel' or formato == 'csv':
        df = pd.DataFrame(list(datos_reporte))
        df.rename(columns={
            'usuario__email': 'Email Vendedor', 'usuario__nombre': 'Nombre',
            'usuario__apellido': 'Apellido', 'numero_ventas': 'Cantidad de Ventas',
            'ingresos_totales': 'Ingresos Totales (Bs.)'
        }, inplace=True)
        
        if formato == 'excel':
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyl') as writer:
                df.to_excel(writer, sheet_name='Ventas_por_Vendedor', index=False)
            output.seek(0)
            response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename_base}.xlsx"'
            return response
        
        elif formato == 'csv':
            csv_data = df.to_csv(index=False, encoding='utf-8')
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename_base}.csv"'
            return response
            
    return HttpResponse(f"Formato '{formato}' no soportado.", status=400)


# --- FUNCIÓN 4: REPORTE DE MÉTODO DE PAGO ---
def generar_reporte_metodo_pago(request, formato, fecha_inicio, fecha_fin):
    
    fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
    fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')

    # 1. Consulta Base
    base_query = Pago.objects.filter(
        estado='completado',
        empresa=request.user.empresa
    )
    pagos_filtrados = base_query.filter(
        fecha__range=[fecha_inicio, fecha_fin]
    )
    
    if not pagos_filtrados.exists():
        return HttpResponse("No se encontraron pagos para este rango.", status=404)

    # 2. Consulta Específica del Reporte
    datos_reporte = pagos_filtrados.values(
        'metodo__nombre'
    ).annotate(
        numero_pagos=Count('id'),
        monto_total=Sum('monto')
    ).order_by('-monto_total')

    if not datos_reporte:
        return HttpResponse("Sin datos para el reporte.", status=404)
        
    filename_base = f"reporte_metodo_pago_DESDE_{fecha_inicio_str}_HASTA_{fecha_fin_str}"

    # 3. Generación de Archivo
    if formato == 'pdf':
        context = {
            'datos_reporte': datos_reporte,
            'fecha_inicio_str': fecha_inicio_str, 'fecha_fin_str': fecha_fin_str,
        }
        html_string = render_to_string('reports/ingresos_por_metodo.html', context)
        pdf_file = HTML(string=html_string).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename_base}.pdf"'
        return response

    elif formato == 'excel' or formato == 'csv':
        df = pd.DataFrame(list(datos_reporte))
        df.rename(columns={
            'metodo__nombre': 'Método de Pago',
            'numero_pagos': 'Cantidad de Pagos',
            'monto_total': 'Monto Total (Bs.)'
        }, inplace=True)
        
        if formato == 'excel':
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Ingresos_por_Metodo', index=False)
            output.seek(0)
            response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename_base}.xlsx"'
            return response
        
        elif formato == 'csv':
            csv_data = df.to_csv(index=False, encoding='utf-8')
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename_base}.csv"'
            return response
            
    return HttpResponse(f"Formato '{formato}' no soportado.", status=400)