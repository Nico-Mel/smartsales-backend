# utils/viewsets.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from utils.permissions import ModulePermission
from utils.logging_utils import log_action 

class SoftDeleteViewSet(viewsets.ModelViewSet):
    """
    Clase base reutilizable que agrega:
    - Filtro automático de registros activos.
    - Asignación automática de empresa si el modelo tiene ese campo.
    - Registro automático en la Bitácora.
    - Acciones para activar y desactivar (soft delete).
    """
    permission_classes = [ModulePermission]

    def get_queryset(self):
        """
        Filtra automáticamente solo los activos y de la empresa del usuario
        """
        queryset = self.queryset
        user = self.request.user

        # Filtra por empresa solo si el modelo tiene ese campo
        if hasattr(self.queryset.model, 'empresa') and getattr(user, 'empresa', None):
            queryset = queryset.filter(empresa=user.empresa)

        # Filtra solo los activos si el modelo tiene "esta_activo"
        if hasattr(self.queryset.model, 'esta_activo'):
            queryset = queryset.filter(esta_activo=True)

        return queryset
    
    def perform_create(self, serializer):
        """Guarda automáticamente la empresa y registra en bitácora"""
        user = self.request.user
        empresa = getattr(user, 'empresa', None)

        # Si el modelo tiene campo empresa, lo agrega
        if hasattr(self.queryset.model, 'empresa') and empresa:
            instance = serializer.save(empresa=empresa)
        else:
            instance = serializer.save()

        log_action(
            user=user,
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
        obj = self.queryset.model.objects.filter(pk=pk).first()
        if not obj:
            return Response(
                {'detail': f'{self.module_name} no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if hasattr(obj, 'esta_activo'):
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
        obj = self.queryset.model.objects.filter(pk=pk).first()
        if not obj:
            return Response({'detail': f'{self.module_name} no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

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