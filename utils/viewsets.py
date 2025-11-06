# 
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from utils.permissions import ModulePermission

class SoftDeleteViewSet(viewsets.ModelViewSet):
    """
    Clase base reutilizable que agrega:
    - acciones para activar/desactivar (soft delete) registros.
    -Integración con permisos por módulo y acción.
    """
    permission_classes = [ModulePermission]

    def get_queryset(self):
        """
        Si deseas filtrar solo los activos, descomenta:
        return self.queryset.filter(esta_activo=True)
        """
        # return self.queryset
        return self.queryset.filter(esta_activo=True)
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        obj = self.get_object()
        obj.esta_activo = False
        obj.save()
        return Response({'detail': 'Desactivado correctamente.'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        obj = self.get_object()
        obj.esta_activo = True
        obj.save()
        return Response({'detail': 'Activado correctamente.'}, status=status.HTTP_200_OK)