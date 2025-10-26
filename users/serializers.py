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
        fields = ['id', 'name', 'description', 'is_active']


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
