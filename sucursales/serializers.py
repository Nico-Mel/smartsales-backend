from rest_framework import serializers
from .models import Departamento, Direccion, Sucursal, StockSucursal
from tenants.models import Empresa
from products.models import Producto


class DepartamentoSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(source="empresa.nombre", read_only=True)

    class Meta:
        model = Departamento
        fields = ["id", "nombre", "empresa", "empresa_nombre"]


class DireccionSerializer(serializers.ModelSerializer):
    departamento_nombre = serializers.CharField(source="departamento.nombre", read_only=True)
    empresa_nombre = serializers.CharField(source="empresa.nombre", read_only=True)
    cliente_email = serializers.CharField(source="cliente.email", read_only=True)

    class Meta:
        model = Direccion
        fields = [
            "id",
            "pais",
            "ciudad",
            "zona",
            "calle",
            "numero",
            "referencia",
            "departamento",
            "departamento_nombre",
            "empresa",
            "empresa_nombre",
            "cliente",
            "cliente_email",
        ]


class SucursalSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(source="empresa.nombre", read_only=True)
    direccion_detalle = DireccionSerializer(source="direccion", read_only=True)

    class Meta:
        model = Sucursal
        fields = [
            "id",
            "nombre",
            "direccion",
            "direccion_detalle",
            "esta_activo",
            "empresa",
            "empresa_nombre",
        ]

    def validate(self, data):
        """
        Verifica que la dirección pertenezca a la misma empresa.
        """
        empresa = data.get("empresa")
        direccion = data.get("direccion")

        if direccion and empresa and direccion.empresa != empresa:
            raise serializers.ValidationError("La dirección pertenece a otra empresa.")
        return data


class StockSucursalSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    sucursal_nombre = serializers.CharField(source="sucursal.nombre", read_only=True)
    empresa_nombre = serializers.CharField(source="empresa.nombre", read_only=True)

    class Meta:
        model = StockSucursal
        fields = [
            "id",
            "producto",
            "producto_nombre",
            "sucursal",
            "sucursal_nombre",
            "stock",
            "empresa",
            "empresa_nombre",
        ]

    def validate(self, data):
        """
        Garantiza que producto, sucursal y empresa correspondan a la misma empresa.
        """
        empresa = data.get("empresa")
        producto = data.get("producto")
        sucursal = data.get("sucursal")

        if producto and empresa and producto.empresa != empresa:
            raise serializers.ValidationError("El producto pertenece a otra empresa.")
        if sucursal and empresa and sucursal.empresa != empresa:
            raise serializers.ValidationError("La sucursal pertenece a otra empresa.")

        return data
