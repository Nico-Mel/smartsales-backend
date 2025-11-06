from bitacora.models import Bitacora
from utils.helpers import get_client_ip

def log_action(user, modulo, accion, descripcion, request):
    """
    Registra una acción en la bitácora del sistema.
    Puede llamarse desde cualquier ViewSet o función.
    """
    Bitacora.objects.create(
        usuario=user,
        modulo=modulo,
        accion=accion,
        descripcion=descripcion,
        ip=get_client_ip(request)
    )
