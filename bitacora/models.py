from django.db import models
from django.conf import settings

# Create your models here.
class Bitacora(models.Model):
    ACCIONES = [
        ('CREAR', 'Crear'),
        ('EDITAR', 'Editar'),
        ('ELIMINAR', 'Eliminar'),
        ('LOGIN', 'Inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
        ('ACTIVAR', 'Activar'),
        ('DESACTIVAR', 'Desactivar'),
        ('OTRO', 'Otro'),
    ]
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    accion = models.CharField(max_length=20, choices=ACCIONES, default='OTRO')
    descripcion = models.TextField()
    ip = models.GenericIPAddressField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bitacora'
        verbose_name = 'Bitácora'
        verbose_name_plural = 'Bitácoras'
        ordering = ['-fecha']

    def __str__(self):
        return f"[{self.modulo}] {self.usuario} → {self.accion} ({self.fecha.strftime('%Y-%m-%d %H:%M')})"
    
    