# products/serializers.py
from rest_framework import serializers
from sucursales.models import Sucursal
from .models import (
    Marca,
    Categoria,
    Producto,
    ProductoCategoria,
    DetalleProducto,
    ImagenProducto,
    Descuento,
    Campania,
)


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = "__all__"


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"


class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenProducto
        fields = "__all__"


class DetalleProductoSerializer(serializers.ModelSerializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    marca = serializers.PrimaryKeyRelatedField(queryset=Marca.objects.all())

    class Meta:
        model = DetalleProducto
        fields = ["id", "producto", "marca", "color", "precio_venta", "esta_activo"]


class ProductoSerializer(serializers.ModelSerializer):
    detalle = DetalleProductoSerializer(read_only=True)
    imagenes = ImagenProductoSerializer(many=True, read_only=True)

    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "descripcion",
            "fecha_creacion",
            "esta_activo",
            "detalle",
            "imagenes",
        ]


class ProductoCategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoCategoria
        fields = "__all__"


class CampaniaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campania
        fields = "__all__"


class DescuentoSerializer(serializers.ModelSerializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    sucursal = serializers.PrimaryKeyRelatedField(queryset=Sucursal.objects.all())
    campania = serializers.PrimaryKeyRelatedField(
        queryset=Campania.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Descuento
        fields = [
            "id",
            "nombre",
            "tipo",
            "monto",
            "porcentaje",
            "producto",
            "sucursal",
            "esta_activo",
            "campania",
        ]

    def validate(self, data):
        """
        Valida que según el tipo de descuento se use el campo correcto.
        - Si tipo = PORCENTAJE → porcentaje debe existir y monto ser nulo.
        - Si tipo = MONTO → monto debe existir y porcentaje ser nulo.
        """
        tipo = data.get("tipo")
        monto = data.get("monto")
        porcentaje = data.get("porcentaje")

        if tipo == "PORCENTAJE":
            if porcentaje is None:
                raise serializers.ValidationError(
                    "Debe especificar un porcentaje para un descuento porcentual."
                )
            data["monto"] = None  # Limpia monto si no aplica

        elif tipo == "MONTO":
            if monto is None:
                raise serializers.ValidationError(
                    "Debe especificar un monto fijo para un descuento de tipo MONTO."
                )
            data["porcentaje"] = None  # Limpia porcentaje si no aplica

        return data
