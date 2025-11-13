# notifications/models.py
from django.db import models

# Create your models here.
class Notificacion(models.Model):
    empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True)
    titulo = models.CharField(max_length=255)
    mensaje = models.TextField()
    fecha_creada = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    usuario = models.ForeignKey('users.User',on_delete=models.CASCADE, related_name ='notificaciones')
    class Meta:
        db_table = 'notificacion'
    
    def __str__(self):
        return f"Notificacion #{self.id} - {self.titulo}"
