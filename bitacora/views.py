# bitacora/views.py
from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Bitacora
from .serializers import BitacoraSerializer
from utils.permissions import ModulePermission

class BitacoraViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Permite consultar los registros de bitácora.
    Solo lectura; no se crean manualmente desde la API.
    """
    queryset = Bitacora.objects.all().select_related('usuario')
    serializer_class = BitacoraSerializer
    permission_classes = [ModulePermission]
    module_name = "Bitacora"
# Create your views here.
