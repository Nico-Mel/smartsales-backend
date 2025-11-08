# shipping/views.py
from django.shortcuts import render
import rest_framework.permissions as permissions
from rest_framework import viewsets
from sucursales.models import Direccion

# Create your views here.
class MisDireccionesViewSet(viewsets.ModelViewSet):
    """
    Un ViewSet especial para que el usuario logueado
    maneje (ver, crear, editar, borrar) SUS PROPIAS direcciones.
    """
    from sucursales.serializers import DireccionSerializer

    serializer_class = DireccionSerializer
    permission_classes = [permissions.IsAuthenticated] # Solo usuarios logueados

    def get_queryset(self):
        # Devuelve solo las direcciones donde 'cliente' sea el usuario
        # que está haciendo la petición (request.user).
        return Direccion.objects.filter(cliente=self.request.user)

    def perform_create(self, serializer):

        serializer.save(cliente=self.request.user)