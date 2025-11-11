from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tenants.models import Empresa
from users.models import User, Role
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny

class PublicRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data

        empresa_nombre = data.get("empresa_nombre")
        if not empresa_nombre:
            return Response({"detail": "El nombre de la empresa es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            empresa = Empresa.objects.get(nombre=empresa_nombre, esta_activo=True)
        except Empresa.DoesNotExist:
            return Response({"detail": "Empresa no encontrada o no activa."}, status=status.HTTP_404_NOT_FOUND)

        try:
            role = Role.objects.get(name="CUSTOMER", empresa=empresa)
        except Role.DoesNotExist:
            return Response({"detail": "Rol 'CUSTOMER' no encontrado para esta empresa."}, status=status.HTTP_404_NOT_FOUND)

        print(f"Rol encontrado: {role.name} para la empresa: {empresa.nombre}")

        user_data = {
            "email": data.get("email"),
            "password": data.get("password"),
            "nombre": data.get("nombre", ""),
            "apellido": data.get("apellido", ""),
            "telefono": data.get("telefono", ""),
            "role_id": role.id,  # Aquí estamos pasando el role_id
            "empresa_id": empresa.id  # Aquí estamos pasando el empresa_id
        }

        print(f"Datos de usuario antes de crear: {user_data}")

        serializer = UserSerializer(data=user_data)

        if serializer.is_valid():
            user = serializer.save()
            print(f"Usuario creado con rol: {user.role.name}, empresa: {user.empresa.nombre}")  # Verifica que el rol y la empresa se asignan correctamente
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        else:
            print(f"Errores al crear el usuario: {serializer.errors}")  # Verifica si hay errores en la creación del usuario
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
