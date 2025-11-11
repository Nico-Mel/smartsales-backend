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
from rest_framework.views import APIView
from utils.viewsets import SoftDeleteViewSet
from notifications.push_service import send_onesignal_notification
class NotificacionTestView(APIView):
    def post(self, request):
        # Obtener el token de OneSignal desde el request
        user = request.user  # Usuario autenticado
        onesignal_token = user.onesignal_player_id

        # Aquí puedes crear la notificación
        titulo = "¡Notificación de prueba!"
        mensaje = "Esta es una notificación enviada desde el backend."

        # Enviar la notificación push a través de OneSignal
        send_onesignal_notification(
            user=user,
            title=titulo,
            message=mensaje,
        )

        return Response({"detail": "Notificación enviada con éxito."}, status=status.HTTP_201_CREATED)
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
        onesignal_token = data.get("onesignal_token")  # Obtener token OneSignal

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
        # Guardar el token de OneSignal si se proporciona
        if onesignal_token:
            user.onesignal_player_id = onesignal_token
            user.save()

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
