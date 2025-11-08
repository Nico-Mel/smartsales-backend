# users/admin_views.py

from django.conf import settings
from django.core.management import call_command
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes # Importa los decoradores
from rest_framework import status
import io
from contextlib import redirect_stdout

# --- VISTA 1: POBLAR CONFIGURACIÓN (seed-config) ---

@api_view(['POST']) # Define que esta vista solo acepta POST
@permission_classes([IsAdminUser]) # Solo Admins
def seed_database_view(request):
    """
    Endpoint (ADMIN + DEBUG) para POBLAR la BD con datos iniciales (Configuración).
    """
    # ¡DOBLE BLOQUEO DE SEGURIDAD!
    if not settings.DEBUG:
        return Response(
            {"error": "Esta acción solo está permitida en modo DEBUG."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    f = io.StringIO()
    with redirect_stdout(f):
        try:
            call_command('seed_users_data') # Llama al seeder de config
            message = "Base de datos poblada con configuración exitosamente."
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


# --- VISTA 2: RESETEAR CONFIGURACIÓN (reset-config) ---

@api_view(['POST']) # Define que esta vista solo acepta POST
@permission_classes([IsAdminUser]) # Solo Admins
def reset_database_view(request):
    """
    Endpoint (ADMIN + DEBUG) para RESETEAR los datos de configuración.
    """
    # ¡DOBLE BLOQUEO DE SEGURIDAD!
    if not settings.DEBUG:
        return Response(
            {"error": "Esta acción solo está permitida en modo DEBUG."},
            status=status.HTTP_403_FORBIDDEN
        )

    f = io.StringIO()
    with redirect_stdout(f):
        try:
            call_command('reset_seed_data') # Llama al reset de config
            message = "Datos de configuración reseteados exitosamente."
        except Exception as e:
            return Response(
                {"error": f"Ocurrió un error al ejecutar 'reset_seed_data': {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    output = f.getvalue()
    return Response({
        "message": message,
        "log": output.split('\n')
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def seed_sample_data_view(request):
    """
    Endpoint (ADMIN + DEBUG) para POBLAR la BD con datos de MUESTRA (Productos, etc).
    """
    if not settings.DEBUG:
        return Response(
            {"error": "Esta acción solo está permitida en modo DEBUG."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    f = io.StringIO()
    with redirect_stdout(f):
        try:
            # Llama al NUEVO comando de sample data
            call_command('seed_sample_data') 
            message = "Base de datos poblada con datos de muestra."
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
@permission_classes([IsAdminUser])
def reset_sample_data_view(request):
    """
    Endpoint (ADMIN + DEBUG) para RESETEAR los datos de MUESTRA.
    """
    if not settings.DEBUG:
        return Response(
            {"error": "Esta acción solo está permitida en modo DEBUG."},
            status=status.HTTP_403_FORBIDDEN
        )

    f = io.StringIO()
    with redirect_stdout(f):
        try:
            # Llama al NUEVO comando de reset sample
            call_command('reset_sample_data') 
            message = "Datos de muestra reseteados exitosamente."
        except Exception as e:
            return Response(
                {"error": f"Ocurrió un error al ejecutar 'reset_sample_data': {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    output = f.getvalue()
    return Response({
        "message": message,
        "log": output.split('\n')
    }, status=status.HTTP_200_OK)