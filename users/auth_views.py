# users/auth_views.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .auth_serializers import CustomTokenObtainPairSerializer

class LoginView(TokenObtainPairView):
    """Genera tokens de acceso (access y refresh)"""
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

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
        return Response({"detail": "Sesión cerrada correctamente."})
