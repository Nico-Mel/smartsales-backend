from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notificacion
from utils.push import send_push_to_user

@receiver(post_save, sender=Notificacion)
def notification_created(sender, instance, created, **kwargs):
    if not created:
        return

    payload = {
        "id": instance.id,
        "titulo": instance.titulo,
        "mensaje": instance.mensaje,
        "fecha": instance.fecha_creada.isoformat()
    }

    # 1. WebSocket notification
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.usuario.id}",
            {
                "type": "notification.message",
                "payload": payload
            }
        )
    except Exception as e:
        print(f"WebSocket error: {e}")

    # 2. Push notification
    try:
        send_push_to_user(
            user=instance.usuario,
            title=instance.titulo,
            body=instance.mensaje,
            data={"notification_id": str(instance.id)}
        )
    except Exception as e:
        print(f"Push notification error: {e}")