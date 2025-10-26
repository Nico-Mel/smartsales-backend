# users/views.py
from django.shortcuts import render

# Create your views here.
# users/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Role, Module, Permission
from .serializers import UserSerializer, RoleSerializer, ModuleSerializer, PermissionSerializer   
from utils.permissions import ModulePermission
# from django.contrib.auth import authenticate
class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD para la gestión de usuarios del sistema.
    Integra control de permisos por módulo y soporte
    para creación directa con asignación de rol.
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    module_name = "User"
    permission_classes = [ModulePermission]

    @action(detail=False, methods=['post'], url_path='registrar')
    def create_user(self, request):
        """
        Permite crear un nuevo usuario indicando el role_id
        """
        data = request.data
        role_id = data.get("role_id")

        if not role_id:
            return Response(
                {"detail":"El campo 'role_id' es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response(
                {"detail":"El rol especificado no existe"},
                status=status.HTTP_404_NOT_FOUND,
            )
        user = User.objects.create_user(
            email=data['email'],
            password=data['password'],
            nombre=data.get('nombre',''),
            apellido=data.get('apellido',''),
            telefono=data.get('telefono',''),
            role=role
        )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    

class RoleViewSet(viewsets.ModelViewSet):
    """
    CRUD para roles del sistema con control de permisos.
    """
    queryset = Role.objects.all().order_by('id')
    serializer_class = RoleSerializer
    permission_classes = [ModulePermission]
    # permission_classes = [permissions.IsAuthenticated]
    module_name = "Role"

class ModuleViewSet(viewsets.ModelViewSet):
    """
    CRUD para los módulos del sistema (entidades protegidas).
    """
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [ModulePermission]
    module_name = "Module"

class PermissionViewSet(viewsets.ModelViewSet):
    """
    CRUD para permisos por rol y módulo con control granular.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [ModulePermission]
    module_name = "Permission"
