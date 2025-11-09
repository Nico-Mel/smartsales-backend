# utils/logging_utils.py
from bitacora.models import Bitacora
from utils.helpers import get_client_ip

def log_action(user, modulo, accion, descripcion, request):
    """
    Registra una acción en la bitácora del sistema con referencia a la empresa del usuario.
    """
    empresa = getattr(user, "empresa", None)

    # 2️⃣ Si no tiene empresa (por ejemplo, superadmin o seeders),
    # intentar obtenerla desde el body de la request
    if empresa is None and hasattr(request, "data"):
        empresa_id = request.data.get("empresa")
        if empresa_id:
            from tenants.models import Empresa
            empresa = Empresa.objects.filter(id=empresa_id).first()

    Bitacora.objects.create(
        usuario=user,
        empresa=empresa,
        modulo=modulo,
        accion=accion,
        descripcion=descripcion,
        ip=get_client_ip(request)
    )
