#sucursales/serializers.py
from rest_framework import serializers
from .models import Departamento, Direccion, Sucursal, StockSucursal
from products.models import Producto # Importamos Producto para el StockSerializer
#no importar nada de shipping para evitar dependencias circulares


class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = "__all__"

class DireccionSerializer(serializers.ModelSerializer):
    departamento = serializers.PrimaryKeyRelatedField(
        queryset=Departamento.objects.all(),
        allow_null=True
    )
    
    class Meta:
        model = Direccion
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.departamento:
            representation['departamento'] = instance.departamento.nombre
        return representation

class SucursalSerializer(serializers.ModelSerializer):
    direccion = DireccionSerializer()

    class Meta:
        model = Sucursal
        fields = ['id', 'nombre', 'direccion', 'esta_activo']

    def create(self, validated_data):
        """
        Maneja la creación de la Sucursal y su Dirección anidada.
        """
        # Saca los datos de la dirección del JSON
        direccion_data = validated_data.pop('direccion')
        
        # 1. Crea la Dirección primero
        direccion = Direccion.objects.create(**direccion_data)
        
        # 2. Crea la Sucursal, asignando la dirección recién creada
        sucursal = Sucursal.objects.create(direccion=direccion, **validated_data)
        
        return sucursal
    
    def update(self, instance, validated_data):
        # Si 'direccion' está en los datos, actualiza la dirección anidada
        if 'direccion' in validated_data:
            direccion_data = validated_data.pop('direccion')
            
            # Actualiza los campos de la dirección existente
            direccion_instance = instance.direccion
            for attr, value in direccion_data.items():
                setattr(direccion_instance, attr, value)
            direccion_instance.save()
            
        # Actualiza los campos de la sucursal (ej. 'nombre', 'esta_activo')
        return super().update(instance, validated_data)


class StockSucursalSerializer(serializers.ModelSerializer):
    producto = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all()
    )
    sucursal = serializers.PrimaryKeyRelatedField(
        queryset=Sucursal.objects.all()
    )

    class Meta:
        model = StockSucursal
        fields = ['id', 'producto', 'sucursal', 'stock']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['producto'] = instance.producto.nombre
        representation['sucursal'] = instance.sucursal.nombre
        return representation