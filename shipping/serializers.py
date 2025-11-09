# shipping/serializers.py
from rest_framework import serializers
from .models import Agencia, Envio
from sucursales.models import Direccion
from users.models import User
from ventas.models import Venta


# ---------------------------------------------------------------------
# 🔹 SERIALIZER: Agencia de Envío
# ---------------------------------------------------------------------
class AgenciaSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(source="empresa.nombre", read_only=True)

    class Meta:
        model = Agencia
        fields = [
            "id",
            "nombre",
            "contacto",
            "telefono",
            "email",
            "esta_activo",
            "empresa",
            "empresa_nombre",
        ]

    def validate(self, data):
        empresa = data.get("empresa")
        nombre = data.get("nombre")
        if empresa and Agencia.objects.filter(empresa=empresa, nombre=nombre).exists():
            raise serializers.ValidationError("Ya existe una agencia con ese nombre en esta empresa.")
        return data


# ---------------------------------------------------------------------
# 🔹 SERIALIZER: Envío
# ---------------------------------------------------------------------
class EnvioSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(source="empresa.nombre", read_only=True)
    venta_numero = serializers.CharField(source="venta.numero_nota", read_only=True)
    cliente_email = serializers.CharField(source="cliente.email", read_only=True)
    direccion_detalle = serializers.SerializerMethodField()
    agencia_nombre = serializers.CharField(source="agencia.nombre", read_only=True)

    class Meta:
        model = Envio
        fields = [
            "id",
            "empresa",
            "empresa_nombre",
            "venta",
            "venta_numero",
            "cliente",
            "cliente_email",
            "direccion_entrega",
            "direccion_detalle",
            "agencia",
            "agencia_nombre",
            "fecha_envio",
            "fecha_entrega",
            "estado",
            "observaciones",
            "esta_activo",
        ]

    def get_direccion_detalle(self, obj):
        if obj.direccion_entrega:
            return str(obj.direccion_entrega)
        return None

    def validate(self, data):
        empresa = data.get("empresa")
        venta = data.get("venta")
        cliente = data.get("cliente")
        agencia = data.get("agencia")

        # 🔹 Validar coherencia multi-tenant
        if venta and empresa and venta.empresa != empresa:
            raise serializers.ValidationError("La venta pertenece a otra empresa.")
        if cliente and empresa and cliente.empresa != empresa:
            raise serializers.ValidationError("El cliente pertenece a otra empresa.")
        if agencia and empresa and agencia.empresa != empresa:
            raise serializers.ValidationError("La agencia pertenece a otra empresa.")
        return data
