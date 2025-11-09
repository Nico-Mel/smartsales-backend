# shipping/models.py
from django.db import models

# Create your models here.
class Agencia(models.Model):
    empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        db_table='agencia'
    
    def __str__(self):
        return self.nombre
    
class Envio(models.Model):
    empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True)
    venta = models.OneToOneField('ventas.Venta', on_delete=models.CASCADE)
    cliente = models.ForeignKey('users.User', on_delete=models.CASCADE)
    direccion_entrega= models.ForeignKey('sucursales.Direccion', on_delete=models.SET_NULL, null=True, blank=True)

    agencia = models.ForeignKey(Agencia, on_delete=models.SET_NULL, null=True)
    
    fecha_envio = models.DateTimeField(blank=True, null=True)
    fecha_entrega = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=50, choices=[
        ('pendiente', 'Pendiente'),
        ('en_transito', 'En Tránsito'),
        ('entregado', 'Entregado'),
        ('devuelto', 'Devuelto'),
    ], default='pendiente')
    observaciones = models.TextField(blank=True, null=True)
    esta_activo = models.BooleanField(default=True)
    class Meta:
        db_table='envio'
    
    def __str__(self):
        return f"Envio #{self.id} - {self.estado}"
