# sucursales/models.py
from django.db import models
from django.conf import settings
#no importar nada de shipping para evitar dependencias circulares
class Departamento(models.Model):
    """
    Representa un departamento o región dentro de una empresa (multi-tenant).
    Ejemplo: 'Santa Cruz', 'La Paz', etc.
    """
    empresa = models.ForeignKey(
        'tenants.Empresa',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='departamentos'
    )
    nombre = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'departamento'
        unique_together = ('empresa', 'nombre')

    def __str__(self):
        if self.empresa:
            return f"{self.nombre} ({self.empresa.nombre})"
        return self.nombre

class Direccion(models.Model):
    """
    Dirección física. Puede pertenecer a una empresa, cliente o sucursal.
    """
    empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True,related_name='direcciones')
    pais= models.CharField(max_length=50, default='Bolivia')
    ciudad = models.CharField(max_length=50)
    zona = models.CharField(max_length=50)
    calle = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    referencia = models.CharField(blank=True, null=True)
    departamento = models.ForeignKey('sucursales.Departamento', on_delete = models.CASCADE, null = True, blank = True)
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="direcciones",
        null=True, 
        blank=True
    )
    class Meta:
        db_table = 'direccion'

    def __str__(self):
        return f"{self.calle} #{self.numero}, {self.zona or '' }, {self.ciudad},{self.departamento}, {self.pais}"

class Sucursal(models.Model):
    empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    direccion = models.OneToOneField(Direccion, on_delete=models.CASCADE, null=True, blank=True)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'sucursal'
        unique_together = ('empresa', 'nombre')

    def __str__(self):
        return self.nombre
class StockSucursal(models.Model):
    empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True)
    stock = models.PositiveBigIntegerField(default=0)
    producto = models.ForeignKey('products.Producto', on_delete=models.CASCADE)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)

    class Meta: 
        unique_together = ('producto', 'sucursal')
        verbose_name = 'Stock en Sucursal'
        verbose_name_plural = 'Stock en Sucursales'
        unique_together = ('empresa', 'producto', 'sucursal')
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.sucursal.nombre} - {self.stock}"
    