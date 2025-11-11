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
from users.models import User
class LoginView(TokenObtainPairView):
    """Genera tokens de acceso (access y refresh)"""
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            email = request.data.get("email")
            onesignal_token = request.data.get("onesignal_token")  # Obtener token OneSignal
            try:
                
                user = User.objects.get(email=email)
                if user and onesignal_token:
                    # Guardar el token de OneSignal en el modelo User
                    user.onesignal_player_id = onesignal_token
                    user.save()

                
                    log_action(
                        user=user,
                        modulo="Autenticación",
                        accion="LOGIN",
                        descripcion=f"Inicio de sesión exitoso de {user.email}",
                        request=request
                    )
                  
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
        token_str = request.data.get("refresh")
        if not token_str:
            return Response({"detail": "refresh token requerido"}, status=400)
        try:
            RefreshToken(token_str).blacklist()
        except Exception:
            return Response({"detail": "refresh inválido"}, status=400)
        user = request.user
        log_action(
            user=user,
            modulo="Autenticación",
            accion="LOGOUT",
            descripcion=f"Cierre de sesión de {user.email}",
            request=request
        )

        return Response({"detail": "Sesión cerrada correctamente."})