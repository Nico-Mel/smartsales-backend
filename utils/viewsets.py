# 
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from utils.permissions import ModulePermission
from utils.logging_utils import log_action 

class SoftDeleteViewSet(viewsets.ModelViewSet):
    """
    Clase base reutilizable que agrega:
    - Acciones para activar/desactivar (soft delete) registros.
    - Integración con permisos por módulo y acción.
    - Registro automático en la Bitácora.
    """
    permission_classes = [ModulePermission]

    def get_queryset(self):
        """
        Si deseas filtrar solo los activos, descomenta:
        return self.queryset.filter(esta_activo=True)
        """
        # return self.queryset
        return self.queryset.filter(esta_activo=True)
    
    def perform_create(self, serializer):
        """Registra la creacion en la bitacora automaticamente"""
        instance = serializer.save()
        log_action(
            user=self.request.user,
            modulo=getattr(self, 'module_name', self.__class__.__name__),
            accion='CREAR',
            descripcion=f"Creó {self.module_name}: {instance}",
            request=self.request
        )

    def perform_update(self, serializer):
        """Registra la actualización en la bitácora."""
        instance = serializer.save()
        log_action(
            user=self.request.user,
            modulo=getattr(self, 'module_name', self.__class__.__name__),
            accion='EDITAR',
            descripcion=f"Editó {self.module_name}: {instance}",
            request=self.request
        )

    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        obj = self.get_object()
        obj.esta_activo = False
        obj.save()
        log_action(
            user=request.user,
            modulo=getattr(self, 'module_name', self.__class__.__name__),
            accion='DESACTIVAR',
            descripcion=f"Desactivó {self.module_name}: {obj}",
            request=request
        )

        return Response({'detail': 'Desactivado correctamente.'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        obj = self.get_object()
        obj.esta_activo = True
        obj.save()
        log_action(
            user=request.user,
            modulo=getattr(self, 'module_name', self.__class__.__name__),
            accion='ACTIVAR',
            descripcion=f"Activó {self.module_name}: {obj}",
            request=request
        )
        return Response({'detail': 'Activado correctamente.'}, status=status.HTTP_200_OK)