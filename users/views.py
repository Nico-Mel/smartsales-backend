# users/views.py
from django.shortcuts import render

# Create your views here.
# users/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Role, Module, Permission
from .serializers import UserSerializer, RoleSerializer, ModuleSerializer, PermissionSerializer, ChangePasswordSerializer  
from utils.permissions import ModulePermission
from utils.viewsets import SoftDeleteViewSet


# from django.contrib.auth import authenticate
class UserViewSet(SoftDeleteViewSet):
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
        Permite crear un nuevo usuario asociado a la misma empresa del usuario actual.
        """
        data = request.data
        role_id = data.get("role_id")

        if not role_id:
            return Response({"detail": "El campo 'role_id' es obligatorio."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({"detail": "El rol especificado no existe."},
                            status=status.HTTP_404_NOT_FOUND)

        empresa = request.user.empresa
        if not empresa:
            return Response({"detail": "El usuario actual no pertenece a ninguna empresa."},
                            status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            email=data['email'],
            password=data['password'],
            nombre=data.get('nombre', ''),
            apellido=data.get('apellido', ''),
            telefono=data.get('telefono', ''),
            role=role,
            empresa=empresa
        )

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

     

class RoleViewSet(SoftDeleteViewSet):
    """
    CRUD de roles por empresa.
    Solo los roles de la empresa del usuario logueado.
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

class PermissionViewSet(SoftDeleteViewSet):
    """
    CRUD de permisos por rol y módulo.
    Aplica filtrado por empresa y bitácora.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [ModulePermission]
    module_name = "Permission"

class ChangePasswordView(APIView):
    """
    Permite al usuario (logueado) cambiar su propia contraseña.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_pass = serializer.validated_data['old_password']
            new_pass = serializer.validated_data['new_password']

            if not user.check_password(old_pass):
                return Response({"detail": "La contraseña actual es incorrecta."}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_pass)
            user.save()
            return Response({"detail": "Contraseña actualizada exitosamente."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
