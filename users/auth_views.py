# users/auth_views.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .auth_serializers import CustomTokenObtainPairSerializer
from utils.logging_utils import log_action
from utils.helpers import get_client_ip
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from .serializers import UserSerializer, UserCreateSerializer

class LoginView(TokenObtainPairView):
    """Genera tokens de acceso (access y refresh)"""
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            email = request.data.get("email")
            try:
                from users.models import User
                user = User.objects.get(email=email)
                if user:
                    try:
                        log_action(
                            user=user,
                            modulo="Autenticación",
                            accion="LOGIN",
                            descripcion=f"Inicio de sesión exitoso de {user.email}",
                            request=request
                        )
                    except Exception as e:
                        print("[ERROR LOG_ACTION]", e)
            except User.DoesNotExist:
                pass
        return response
class RefreshView(TokenRefreshView):
    """Refresca el access token"""
    permission_classes = [AllowAny]

class LogoutView(APIView):
    """Revoca el refresh token (blacklisting)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Obtener el refresh token del usuario actual, NO del request body
            refresh_token = RefreshToken.for_user(request.user)
            refresh_token.blacklist()
            
            user = request.user
            log_action(
                user=user,
                modulo="Autenticación",
                accion="LOGOUT", 
                descripcion=f"Cierre de sesión de {user.email}",
                request=request
            )
            
            return Response({"detail": "Sesión cerrada correctamente."})
            
        except Exception as e:
            return Response({"detail": "Error al cerrar sesión"}, status=400)
        
class UserProfileView(RetrieveAPIView):
    """
    Devuelve el perfil del usuario autenticado (el endpoint /me).
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Simplemente devuelve el usuario de la petición
        return self.request.user
    
class RegisterView(CreateAPIView):
    """
    Crea un nuevo usuario.
    """
    permission_classes = [AllowAny] 
    serializer_class = UserCreateSerializer