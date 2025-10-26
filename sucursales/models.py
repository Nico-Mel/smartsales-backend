from django.db import models

class Sucursal(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'sucursal'

    def __str__(self):
        return self.nombre
