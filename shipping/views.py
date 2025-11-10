# shipping/views.py
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from utils.viewsets import SoftDeleteViewSet
from utils.permissions import ModulePermission
from utils.logging_utils import log_action

from .models import Agencia, Envio
from .serializers import AgenciaSerializer, EnvioSerializer
from sucursales.models import Direccion
from sucursales.serializers import DireccionSerializer
from ventas.models import Venta
from users.models import User

class MisDireccionesViewSet(viewsets.ModelViewSet):
    """
    Un ViewSet especial para que el usuario logueado
    maneje (ver, crear, editar, borrar) SUS PROPIAS direcciones.
    """
    serializer_class = DireccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Direccion.objects.none()  # <-- Devuelve una lista vacía si es anónimo
        return Direccion.objects.filter(cliente=self.request.user)

    def perform_create(self, serializer):
        empresa = getattr(self.request.user, "empresa", None)
        serializer.save(cliente=self.request.user, empresa=empresa)

        # 🔹 Registrar acción en bitácora
        
        log_action(
            user=self.request.user,
            modulo="Direccion",
            accion="CREAR",
            descripcion=f"Creó nueva dirección del usuario {self.request.user.email}",
            request=self.request,
        )

# ---------------------------------------------------------------------
# 🔹 ViewSet: Agencia de Envío
# ---------------------------------------------------------------------
class AgenciaViewSet(SoftDeleteViewSet):
    queryset = Agencia.objects.all().order_by("nombre")
    serializer_class = AgenciaSerializer
    module_name = "Agencia"


# ---------------------------------------------------------------------
# 🔹 ViewSet: Envíos
# ---------------------------------------------------------------------
class EnvioViewSet(SoftDeleteViewSet):
    queryset = Envio.objects.all().order_by("-fecha_envio")
    serializer_class = EnvioSerializer
    module_name = "Envio"

    @action(detail=False, methods=["post"], url_path="registrar")
    def registrar_envio(self, request):
        user = request.user
        empresa = getattr(user, "empresa", None)
        data = request.data

        venta_id = data.get("venta")
        agencia_id = data.get("agencia")
        direccion_id = data.get("direccion_entrega")

        # Validar venta
        try:
            venta = Venta.objects.get(id=venta_id, empresa=empresa)
        except Venta.DoesNotExist:
            return Response({"detail": "Venta no encontrada o pertenece a otra empresa."}, status=404)

        # Validar agencia
        try:
            agencia = Agencia.objects.get(id=agencia_id, empresa=empresa)
        except Agencia.DoesNotExist:
            return Response({"detail": "Agencia no encontrada o pertenece a otra empresa."}, status=404)

        # Validar dirección
        direccion = None
        if direccion_id:
            from sucursales.models import Direccion
            try:
                direccion = Direccion.objects.get(id=direccion_id, empresa=empresa)
            except Direccion.DoesNotExist:
                return Response({"detail": "Dirección no encontrada o pertenece a otra empresa."}, status=404)

        # Crear el envío
        envio = Envio.objects.create(
            empresa=empresa,
            venta=venta,
            cliente=venta.usuario,
            direccion_entrega=direccion,  # ✅ ahora es instancia
            agencia=agencia,
            fecha_envio=data.get("fecha_envio"),
            fecha_entrega=data.get("fecha_entrega"),
            estado=data.get("estado", "pendiente"),
            observaciones=data.get("observaciones", ""),
        )

        # Registrar en bitácora
        log_action(
            user=user,
            modulo=self.module_name,
            accion="CREAR",
            descripcion=f"Registró envío para venta #{venta.numero_nota} ({agencia.nombre})",
            request=request,
        )

        return Response(EnvioSerializer(envio).data, status=status.HTTP_201_CREATED)
