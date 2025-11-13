# users/serializers.py
from rest_framework import serializers
from .models import User, Role, Module, Permission


class RoleSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'display_name', 'description']

    def get_display_name(self, obj):
        return obj.display_name


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'name', 'description', 'esta_activo']


class PermissionSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    module = ModuleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), source='role', write_only=True)
    module_id = serializers.PrimaryKeyRelatedField(queryset=Module.objects.all(), source='module', write_only=True)

    class Meta:
        model = Permission
        fields = ['id', 'role', 'module', 'can_view', 'can_create', 'can_update', 'can_delete', 'role_id', 'module_id']


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), source='role', write_only=True, required=False, allow_null=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'nombre', 'apellido', 'telefono', 'role', 'role_id', 'password']

    def create(self, validated_data):
        pwd = validated_data.pop('password', None)
        user = super().create(validated_data)
        if pwd:
            user.set_password(pwd)
            user.save()
        return user

    def update(self, instance, validated_data):
        pwd = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if pwd:
            user.set_password(pwd)
            user.save()
        return user

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model() # (Asumo que tienes un User model custom)

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # ¡Asegúrate de incluir todos los campos del formulario!
        fields = ('email', 'nombre', 'apellido', 'telefono', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # ¡Esta es la parte clave! Usamos create_user.
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            nombre=validated_data.get('nombre', ''),
            apellido=validated_data.get('apellido', ''),
            telefono=validated_data.get('telefono', None),

            role_id=4,
            empresa_id=1
        )
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    def validate_new_password(self, value):
        # (Aquí puedes añadir validación de 8 caracteres, etc. si quieres)
        return value