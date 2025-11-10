from rest_framework import serializers
from .models import Metodo_pago, Pago, Venta, DetalleVenta
from users.models import User
from products.models import Producto
from tenants.models import Empresa


# ---------------------------------------------------------------------
# 🔹 SERIALIZER: Método de Pago
# ---------------------------------------------------------------------
class MetodoPagoSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(source="empresa.nombre", read_only=True)

    class Meta:
        model = Metodo_pago
        fields = [
            "id",
            "nombre",
            "descripcion",
            "proveedor",
            "esta_activo",
            "empresa",
            "empresa_nombre",
        ]

    def validate(self, data):
        empresa = data.get("empresa")
        nombre = data.get("nombre")
        if empresa and Metodo_pago.objects.filter(empresa=empresa, nombre=nombre).exists():
            raise serializers.ValidationError("Ya existe un método de pago con ese nombre en esta empresa.")
        return data


# ---------------------------------------------------------------------
# 🔹 SERIALIZER: Pago
# ---------------------------------------------------------------------
class PagoSerializer(serializers.ModelSerializer):
    metodo_nombre = serializers.CharField(source="metodo.nombre", read_only=True)
    empresa_nombre = serializers.CharField(source="empresa.nombre", read_only=True)

    class Meta:
        model = Pago
        fields = [
            "id",
            "metodo",
            "metodo_nombre",
            "monto",
            "estado",
            "fecha",
            "referencia",
            "empresa",
            "empresa_nombre",
        ]

    def validate(self, data):
        empresa = data.get("empresa")
        metodo = data.get("metodo")

        if metodo and empresa and metodo.empresa != empresa:
            raise serializers.ValidationError("El método de pago pertenece a otra empresa.")
        return data


# ---------------------------------------------------------------------
# 🔹 SERIALIZER: Detalle de Venta
# ---------------------------------------------------------------------
class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    empresa_nombre = serializers.CharField(source="empresa.nombre", read_only=True)

    class Meta:
        model = DetalleVenta
        fields = [
            "id",
            "venta",
            "producto",
            "producto_nombre",
            "cantidad",
            "precio_unitario",
            "subtotal",
            "empresa",
            "empresa_nombre",
        ]
        read_only_fields = ["subtotal"]

    def validate(self, data):
        empresa = data.get("empresa")
        producto = data.get("producto")
        venta = data.get("venta")

        if producto and empresa and producto.empresa != empresa:
            raise serializers.ValidationError("El producto pertenece a otra empresa.")
        if venta and empresa and venta.empresa != empresa:
            raise serializers.ValidationError("La venta pertenece a otra empresa.")
        return data


# ---------------------------------------------------------------------
# 🔹 SERIALIZER: Venta (con detalles anidados)
# ---------------------------------------------------------------------
class VentaSerializer(serializers.ModelSerializer):
    usuario_email = serializers.CharField(source="usuario.email", read_only=True)
    empresa_nombre = serializers.CharField(source="empresa.nombre", read_only=True)
    pago_detalle = PagoSerializer(source="pago", read_only=True)
    detalles = DetalleVentaSerializer(many=True, read_only=True)

    class Meta:
        model = Venta
        fields = [
            "id",
            "numero_nota",
            "usuario",
            "usuario_email",
            "sucursal", 
            "sucursal_id",
            "canal",
            "pago",
            "pago_detalle",
            "fecha",
            "total",
            "estado",
            "esta_activo",
            "empresa",
            "empresa_nombre",
            "detalles",
        ]

    def validate(self, data):
        empresa = data.get("empresa")
        pago = data.get("pago")
        usuario = data.get("usuario")
        sucursal = data.get("sucursal")

        if pago and empresa and pago.empresa != empresa:
            raise serializers.ValidationError("El pago pertenece a otra empresa.")
        if usuario and empresa and usuario.empresa != empresa:
            raise serializers.ValidationError("El usuario pertenece a otra empresa.")
        if sucursal and empresa and sucursal.empresa != empresa: 
            raise serializers.ValidationError("La sucursal pertenece a otra empresa.")
        return data

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["estado"] = instance.estado.capitalize()
        return rep
