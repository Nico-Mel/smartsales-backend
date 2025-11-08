# bitacora/serializers.py
from rest_framework import serializers
from .models import Bitacora
from users.serializers import UserSerializer

class BitacoraSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)

    class Meta:
        model = Bitacora
        fields = ['id', 'usuario', 'modulo', 'accion', 'descripcion', 'ip', 'fecha']