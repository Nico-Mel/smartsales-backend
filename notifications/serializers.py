from rest_framework import serializers
from .models import Notificacion
from users.models import User


class NotificacionSerializer(serializers.ModelSerializer):
    """
    Serializador principal para las notificaciones.
    Diseñado para permitir:
      - creación de notificaciones desde el backend (admin o sistema)
      - envío futuro como push notification
      - visualización filtrada por usuario
    """
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
        read_only_fields = ["fecha_creada"]

    # ------------------------------------------------------------------
    # 🔹 Validaciones
    # ------------------------------------------------------------------
    def validate(self, data):
        empresa = data.get("empresa")
        usuario = data.get("usuario")

        if usuario and empresa and usuario.empresa != empresa:
            raise serializers.ValidationError(
                "El usuario no pertenece a la misma empresa de la notificación."
            )
        return data

    # ------------------------------------------------------------------
    # 🔹 Creación de notificación (lista para push)
    # ------------------------------------------------------------------
    def create(self, validated_data):
        notificacion = super().create(validated_data)

        # 🔸 Lugar para integrar push notifications
        #   (por ejemplo, Firebase Cloud Messaging o OneSignal)
        #   Aquí podrías llamar a una función como:
        #   send_push_notification(user=notificacion.usuario, titulo=..., mensaje=...)
        #
        #   Ejemplo:
        #   from utils.push_service import send_push_notification
        #   send_push_notification(notificacion.usuario, notificacion.titulo, notificacion.mensaje)

        return notificacion
