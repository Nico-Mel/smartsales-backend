from rest_framework import serializers
from .models import ReportDefinition, ReportRun

class ReportDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportDefinition
        fields = '__all__'

class ReportRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportRun
        fields = '__all__'
        read_only_fields = ('estado','archivo','started_at','finished_at','error')