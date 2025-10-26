# users/auth_serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extiende el token JWT para incluir datos adicionales del usuario (rol, nombre, etc.)
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["role"] = user.role.name if user.role else None
        token["nombre"] = user.nombre
        token["apellido"] = user.apellido
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            "id": self.user.id,
            "email": self.user.email,
            "role": self.user.role.name if self.user.role else None,
            "nombre": self.user.nombre,
            "apellido": self.user.apellido,
        })
        return data
