import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return

        # Crear grupo único para el usuario
        self.group_name = f"user_{self.user.id}"
        
        # Unirse al grupo
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Abandonar grupo
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    # Recibir mensaje desde WebSocket
    async def receive(self, text_data):
        pass  # Opcional: manejar mensajes del cliente

    # Enviar notificación al WebSocket
    async def notification_message(self, event):
        # Enviar mensaje al WebSocket
        await self.send(text_data=json.dumps(event["payload"]))