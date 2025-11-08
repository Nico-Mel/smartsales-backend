# products/serializers.py
from rest_framework import serializers
from sucursales.models import Sucursal
from .models import (
    Marca,
    Categoria,
    SubCategoria,      
    Producto,
    DetalleProducto,
    ImagenProducto,
    Descuento,
    Campania,
)


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = "__all__"


class SubCategoriaSerializer(serializers.ModelSerializer): 
    """
    Nivel 2: Ej. "Licuadoras").
    """
    categoria = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all())

    class Meta:
        model = SubCategoria
        fields = "__all__"
        
    def to_representation(self, instance):

        representation = super().to_representation(instance)
        representation['categoria'] = instance.categoria.nombre
        return representation


class CategoriaSerializer(serializers.ModelSerializer): # <-- MODIFICADO
    """
    Nivel 1: Ej. "ELECTROHOGAR".
    """
    subcategorias = SubCategoriaSerializer(many=True, read_only=True)

    class Meta:
        model = Categoria
        fields = ["id", "nombre", "descripcion", "esta_activo", "subcategorias"]


class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenProducto
        fields = "__all__"


class DetalleProductoSerializer(serializers.ModelSerializer): # <-- CAMBIADO
    class Meta:
        model = DetalleProducto
        # "Ficha Técnica"
        fields = [
            "id",
            "producto",
            "potencia",
            "velocidades",
            "voltaje",
            "aire_frio",
            "tecnologias",
            "largo_cable",
        ]

class ProductoSerializer(serializers.ModelSerializer): 

    detalle = DetalleProductoSerializer(read_only=True)
    
    imagenes = ImagenProductoSerializer(many=True, read_only=True)

    marca = serializers.PrimaryKeyRelatedField(
        queryset=Marca.objects.all(), allow_null=True, required=False
    )
    subcategoria = serializers.PrimaryKeyRelatedField(
        queryset=SubCategoria.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "sku",            
            "precio_venta",  
            "descripcion",
            "marca",          
            "subcategoria",   
            "fecha_creacion",
            "esta_activo",
            "detalle",
            "imagenes",
        ]

    def to_representation(self, instance):

        representation = super().to_representation(instance)
        if instance.marca:
            representation['marca'] = instance.marca.nombre
        if instance.subcategoria:
            representation['subcategoria'] = str(instance.subcategoria)
        return representation


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
