# users/admin_views.py

from django.conf import settings
from django.core.management import call_command
from rest_framework.response import Response
# ¡Quitamos IsAdminUser y permission_classes!
from rest_framework.decorators import api_view 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
import io
from contextlib import redirect_stdout

# --- VISTA 1: POBLAR CONFIGURACIÓN (seed_users_data) ---

@api_view(['POST'])
# @permission_classes([IsAdminUser]) # <-- ¡VALIDACIÓN ELIMINADA!
@permission_classes([AllowAny])
def seed_database_view(request):
    """
    Endpoint (DEBUG) para POBLAR la BD con datos iniciales
    (Empresas, Roles, Admin, Permisos, etc.).
    Ejecuta: 'seed_users_data'
    """
    if not settings.DEBUG:
        return Response(
            {"error": "Esta acción solo está permitida en modo DEBUG."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    f = io.StringIO()
    with redirect_stdout(f):
        try:
            call_command('seed_users_data') 
            message = "Base de datos poblada con configuración (usuarios/empresas) exitosamente."
        except Exception as e:
            return Response(
                {"error": f"Ocurrió un error al ejecutar 'seed_users_data': {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    output = f.getvalue()
    return Response({
        "message": message,
        "log": output.split('\n')
    }, status=status.HTTP_200_OK)


# --- VISTA 2: POBLAR DATOS DE MUESTRA (seed_sample_data) ---

@api_view(['POST'])
@permission_classes([AllowAny])
# @permission_classes([IsAdminUser]) # <-- ¡VALIDACIÓN ELIMINADA!
def seed_sample_data_view(request):
    """
    Endpoint (DEBUG) para POBLAR la BD con datos de MUESTRA
    (Productos, Stock, etc.).
    Ejecuta: 'seed_sample_data'
    """
    if not settings.DEBUG:
        return Response(
            {"error": "Esta acción solo está permitida en modo DEBUG."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    f = io.StringIO()
    with redirect_stdout(f):
        try:
            call_command('seed_sample_data') 
            message = "Base de datos poblada con datos de muestra (productos) exitosamente."
        except Exception as e:
            return Response(
                {"error": f"Ocurrió un error al ejecutar 'seed_sample_data': {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    output = f.getvalue()
    return Response({
        "message": message,
        "log": output.split('\n')
    }, status=status.HTTP_200_OK)

# --- VISTA 2: POBLAR DATOS DE MUESTRA (seed_sample_data) ---

@api_view(['POST'])
@permission_classes([AllowAny])
# @permission_classes([IsAdminUser]) # <-- ¡VALIDACIÓN ELIMINADA!
def seed_products_data_view(request):
    """
    Endpoint (DEBUG) para POBLAR la BD con datos de MUESTRA
    (Productos, Stock, etc.).
    Ejecuta: 'seed_sample_data'
    """
    if not settings.DEBUG:
        return Response(
            {"error": "Esta acción solo está permitida en modo DEBUG."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    f = io.StringIO()
    with redirect_stdout(f):
        try:
            call_command('seed_products_data') 
            message = "Base de datos poblada con datos de muestra (productos) exitosamente."
        except Exception as e:
            return Response(
                {"error": f"Ocurrió un error al ejecutar 'seed_sample_data': {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    output = f.getvalue()
    return Response({
        "message": message,
        "log": output.split('\n')
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
# @permission_classes([IsAdminUser]) # <-- ¡VALIDACIÓN ELIMINADA!
def seed_sales_data_view(request):
    """
    Endpoint (DEBUG) para POBLAR la BD con datos de MUESTRA
    Ejecuta: 'seed_sales_data'
    """
    if not settings.DEBUG:
        return Response(
            {"error": "Esta acción solo está permitida en modo DEBUG."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    f = io.StringIO()
    with redirect_stdout(f):
        try:
            call_command('seed_sales_data') 
            message = "Base de datos poblada con datos de muestra (productos) exitosamente."
        except Exception as e:
            return Response(
                {"error": f"Ocurrió un error al ejecutar 'seed_sample_data': {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    output = f.getvalue()
    return Response({
        "message": message,
        "log": output.split('\n')
    }, status=status.HTTP_200_OK)

# --- VISTA 3: RESETEO TOTAL (reset_all_data) ---

@api_view(['POST'])
@permission_classes([AllowAny])
# @permission_classes([IsAdminUser]) # <-- ¡VALIDACIÓN ELIMINADA!
def reset_all_data_view(request):
    """
    Endpoint (DEBUG) para RESETEAR TOTALMENTE la base de datos.
    TRUNCATE a todas las tablas.
    Ejecuta: 'reset_all_data'
    """
    if not settings.DEBUG:
        return Response(
            {"error": "Esta acción solo está permitida en modo DEBUG."},
            status=status.HTTP_403_FORBIDDEN
        )
        
    f = io.StringIO()
    with redirect_stdout(f):
        try:
            # Llama al comando con el flag para saltar la confirmación
            call_command('reset_all_data', no_input=True) 
            message = "RESET TOTAL de la base de datos completado."
        except Exception as e:
            return Response(
                {"error": f"Ocurrió un error al ejecutar 'reset_all_data': {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    output = f.getvalue()
    return Response({
        "message": message,
        "log": output.split('\n')
    }, status=status.HTTP_200_OK)