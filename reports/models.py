from django.db import models
from tenants.models import Empresa
from django.conf import settings

class ReportDefinition(models.Model):
    empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    descripcion = models.TextField(blank=True)
    # tipo: 'ventas', 'stock', 'custom_sql', etc.
    tipo = models.CharField(max_length=50)
    parametros = models.JSONField(default=dict, blank=True)  # definición de filtros disponibles
    esta_activo = models.BooleanField(default=True)

    class Meta:
        db_table = "report_definition"

class ReportRun(models.Model):
    report = models.ForeignKey(ReportDefinition, on_delete=models.CASCADE, related_name='runs')
    empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True)
    solicitado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    filtros = models.JSONField(default=dict, blank=True)
    formato = models.CharField(max_length=10, default='csv')  # csv, xlsx, pdf
    estado = models.CharField(max_length=20, default='PENDING')  # PENDING, RUNNING, DONE, FAILED
    archivo = models.FileField(upload_to='reports/', null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "report_run"
# Create your models here.
