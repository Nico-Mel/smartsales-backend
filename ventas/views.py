# ventas/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from utils.viewsets import SoftDeleteViewSet
from utils.permissions import ModulePermission
from utils.logging_utils import log_action

from .models import Metodo_pago, Pago, Venta, DetalleVenta
from .serializers import (
    MetodoPagoSerializer,
    PagoSerializer,
    VentaSerializer,
    DetalleVentaSerializer,
)
from products.models import Producto


# ---------------------------------------------------------------------
# 🔹 ViewSet: Métodos de Pago
# ---------------------------------------------------------------------
class MetodoPagoViewSet(SoftDeleteViewSet):
    queryset = Metodo_pago.objects.all().order_by("nombre")
    serializer_class = MetodoPagoSerializer
    module_name = "MetodoPago"


# ---------------------------------------------------------------------
# 🔹 ViewSet: Pagos
# ---------------------------------------------------------------------
class PagoViewSet(SoftDeleteViewSet):
    queryset = Pago.objects.all().order_by("-fecha")
    serializer_class = PagoSerializer
    module_name = "Pago"


# ---------------------------------------------------------------------
# 🔹 ViewSet: Ventas
# ---------------------------------------------------------------------
class VentaViewSet(SoftDeleteViewSet):
    queryset = Venta.objects.all().order_by("-fecha")
    serializer_class = VentaSerializer
    module_name = "Venta"

    @action(detail=True, methods=["get"], url_path="detalles")
    def obtener_detalles(self, request, pk=None):
        """
        Obtiene los detalles de una venta específica.
        """
        venta = self.get_object()
        detalles = venta.detalles.all()
        serializer = DetalleVentaSerializer(detalles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="registrar")
    def registrar_venta(self, request):
        """
        Permite registrar una nueva venta con sus detalles.
        """
        data = request.data
        user = request.user
        empresa = getattr(user, "empresa", None)

        # Validaciones básicas
        detalles = data.get("detalles", [])
        if not detalles:
            return Response({"detail": "Debe incluir al menos un producto."}, status=400)

        # Crear el pago si viene incluido
        pago_data = data.get("pago")
        pago_instance = None
        if pago_data:
            pago_serializer = PagoSerializer(data=pago_data)
            pago_serializer.is_valid(raise_exception=True)
            pago_instance = pago_serializer.save(empresa=empresa)

        # Crear la venta
        venta = Venta.objects.create(
            empresa=empresa,
            usuario=user,
            pago=pago_instance,
            total=data.get("total", 0),
            estado=data.get("estado", "pendiente"),
        )

        # Crear los detalles
        for det in detalles:
            producto_id = det.get("producto")
            cantidad = det.get("cantidad")
            precio = det.get("precio_unitario")

            try:
                producto = Producto.objects.get(id=producto_id, empresa=empresa)
            except Producto.DoesNotExist:
                return Response(
                    {"detail": f"Producto ID {producto_id} no encontrado o pertenece a otra empresa."},
                    status=404,
                )

            DetalleVenta.objects.create(
                empresa=empresa,
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio,
                subtotal=cantidad * float(precio),
            )

        log_action(
            user=user,
            modulo=self.module_name,
            accion="CREAR",
            descripcion=f"Registró la venta #{venta.numero_nota} por un total de {venta.total}",
            request=request,
        )

        return Response(VentaSerializer(venta).data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------
# 🔹 ViewSet: Detalles de Venta
# ---------------------------------------------------------------------
class DetalleVentaViewSet(SoftDeleteViewSet):
    queryset = DetalleVenta.objects.all().order_by("venta__id")
    serializer_class = DetalleVentaSerializer
    module_name = "DetalleVenta"

