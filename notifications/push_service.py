# utils/push_service.py
import requests
from django.conf import settings

def send_onesignal_notification(user, title, message, data_extra=None):
    """
    Envía una notificación push a un usuario específico mediante OneSignal.

    Args:
        user: Instancia del modelo User (debe tener un token OneSignal registrado)
        title (str): Título de la notificación
        message (str): Cuerpo o contenido de la notificación
        data_extra (dict, opcional): Datos adicionales para el cliente móvil

    Returns:
        dict: Resultado del envío
    """
    # Obtener la REST API Key y App ID de OneSignal desde las configuraciones
    onesignal_api_key = settings.ONESIGNAL_REST_API_KEY
    onesignal_app_id = settings.ONESIGNAL_APP_ID

    # Validar que la API Key esté configurada
    if not onesignal_api_key:
        print("[⚠️ NOTIFICACIONES] No se encontró la clave REST API Key de OneSignal.")
        return {"success": False, "error": "No OneSignal API key configured"}

    # Obtener el token OneSignal del usuario
    token = getattr(user, "onesignal_player_id", None)
    if not token:
        print(f"[⚠️ NOTIFICACIONES] El usuario {user.email} no tiene token OneSignal registrado.")
        return {"success": False, "error": "No OneSignal token for user"}

    # Construir el payload de la notificación
    payload = {
        "app_id": onesignal_app_id,
        "include_player_ids": [token],  # Token del dispositivo
        "headings": {"en": title},
        "contents": {"en": message},
        "data": data_extra or {},
        "priority": "high"
    }

    # Enviar la solicitud POST a OneSignal
    url = "https://onesignal.com/api/v1/notifications"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {onesignal_api_key}"
    }

    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    if response.status_code == 200:
        print(f"[✅ NOTIFICACIONES] Notificación enviada a {user.email}")
        return {"success": True, "response": result}
    else:
        print(f"[❌ NOTIFICACIONES] Error al enviar la notificación: {response.text}")
        return {"success": False, "response": result}
