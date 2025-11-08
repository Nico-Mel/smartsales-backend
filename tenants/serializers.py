from rest_framework import serializers
from .models import Empresa, Plan
class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class EmpresaSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.filter(activo=True),source='plan',write_only=True)

    class Meta:
        model = Empresa
        fields = [
            'id',
            'nombre',
            'nit',
            'direccion',
            'plan',         # muestra los detalles del plan
            'plan_id',
            'logo',
            'esta_activo',
            'fecha_registro'
        ]
        read_only_fields = ['fecha_registro']

    def validate_plan(self, value):
        """
        Validar que el plan ingresado sea uno de los definidos.
        """
        PLANES_VALIDOS = ['BASIC', 'PREMIUM', 'ENTERPRISE']
        if value not in PLANES_VALIDOS:
            raise serializers.ValidationError(
                f"Plan no válido. Debe ser uno de: {', '.join(PLANES_VALIDOS)}"
            )
        return value
