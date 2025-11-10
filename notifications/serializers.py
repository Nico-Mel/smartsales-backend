from rest_framework import serializers
from .models import Notificacion

class NotificacionSerializer(serializers.ModelSerializer):
    usuario_email = serializers.CharField(source="usuario.email", read_only=True)
    empresa_nombre = serializers.CharField(source="empresa.nombre", read_only=True)

    class Meta:
        model = Notificacion
        fields = [
            "id",
            "empresa",
            "empresa_nombre",
            "usuario",
            "usuario_email",
            "titulo",
            "mensaje",
            "fecha_creada",
            "leida",
        ]
        read_only_fields = ["fecha_creada", "empresa_nombre", "usuario_email"]