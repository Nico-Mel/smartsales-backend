# tenants/models.py
from django.db import models

# Create your models here.
class Empresa(models.Model):
    nombre = models.CharField(max_length=150)
    nit = models.CharField(max_length=50, unique=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    plan = models.ForeignKey('tenants.Plan', on_delete=models.SET_NULL, null=True, blank=True)
    logo = models.ImageField(upload_to='empresas/', blank=True, null=True)
    esta_activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta: 
        db_table = 'Empresa'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nombre 

class Plan(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    max_usuarios = models.PositiveBigIntegerField(null=True, blank=True)
    max_productos = models.PositiveIntegerField(null=True, blank=True)
    max_ventas_mensuales = models.PositiveIntegerField(null=True, blank=True)
    almacenamiento_gb = models.PositiveIntegerField(default=1)
    precio_mensual= models.DecimalField(max_digits=10, decimal_places=2, default=0)
    permite_reportes_ia = models.BooleanField(default=False)
    permite_exportar_excel = models.BooleanField(default=False)
    permite_notificaciones_push = models.BooleanField(default=False)
    soporte_prioritario= models.BooleanField(default=False)
    esta_activo = models.BooleanField(default=True)
    prediccion_ventas = models.BooleanField(default=True)

    class Meta: 
        db_table = 'plan'
    
    def __str__(self):
        return f"{self.nombre} (${self.precio_mensual}/mes)" 
    
