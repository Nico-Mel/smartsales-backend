# users/views.py
from django.shortcuts import render

# Create your views here.
# users/views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Role, Module, Permission
from .serializers import UserSerializer, RoleSerializer, ModuleSerializer, PermissionSerializer   
from utils.permissions import ModulePermission

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    module_name = "User"

    def get_permissions(self):
        if self.action == 'login':
            return [permissions.AllowAny()]
        return [ModulePermission()]

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny],url_path='login', url_name='login')
    def login(self, request):
        from django.contrib.auth import authenticate
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'detail': 'Credenciales inválidas'}, status=401)

    @action(detail=False, methods=['post'],url_path='logout', url_name='logout')
    def logout(self, request):
        return Response({'detail': 'Sesión cerrada'})
    
    @action(detail=False, methods=['post'])
    def create_user(self, request):
        data = request.data
        role_id = data.get('role_id')
        if not role_id:
            return Response({'detail': 'role_id es requerido'}, status=400)

        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({'detail': 'Rol no encontrado'}, status=404)

        user = User.objects.create_user(
            email=data['email'],
            password=data['password'],
            nombre=data.get('nombre', ''),
            apellido=data.get('apellido', ''),
            telefono=data.get('telefono', ''),
            role=role
        )
        return Response(UserSerializer(user).data, status=201)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [ModulePermission]
    module_name = "Module"

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
