# notifications/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from utils.viewsets import SoftDeleteViewSet
from .models import Notificacion
from .serializers import NotificacionSerializer
from .push_service import send_onesignal_notification  # Asegúrate de que el servicio esté implementado
from rest_framework.views import APIView
class NotificacionTestView(APIView):
    def post(self, request):
        # Crear una notificación de prueba
        notificacion_data = {
            "titulo": "¡Notificación de prueba!",
            "mensaje": "Esta es una notificación enviada desde el backend.",
            "usuario": request.user.id,  # Suponiendo que tienes el usuario autenticado
        }

        serializer = NotificacionSerializer(data=notificacion_data)
        if serializer.is_valid():
            notificacion = serializer.save()

            # Enviar la notificación push a través de OneSignal
            send_onesignal_notification(
                user=notificacion.usuario,
                title=notificacion.titulo,
                message=notificacion.mensaje,
            )

            return Response({"detail": "Notificación enviada con éxito."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NotificacionViewSet(SoftDeleteViewSet):
    queryset = Notificacion.objects.all().order_by("-fecha_creada")
    serializer_class = NotificacionSerializer
    module_name = "Notificacion"

    def perform_create(self, serializer):
        user = self.request.user
        empresa = getattr(user, "empresa", None)
        notificacion = serializer.save(empresa=empresa)

        # Enviar notificación push con OneSignal
        send_onesignal_notification(
            user=notificacion.usuario,
            title=notificacion.titulo,
            message=notificacion.mensaje,
        )

        return notificacion
