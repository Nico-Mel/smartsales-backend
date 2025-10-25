# products/models.py
from django.db import models


# Create your models here.
class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        db_table = "marca"

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        db_table = "categoria"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        db_table = "producto"

    def __str__(self):
        return self.nombre


class ProductoCategoria(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        db_table = "producto_categoria"
        unique_together = ("producto", "categoria")

    def __str__(self):
        return f"{self.producto.nombre}-{self.categoria.nombre}"


class DetalleProducto(models.Model):
    producto = models.OneToOneField(
        Producto, on_delete=models.CASCADE, related_name="detalle"
    )
    # cual es la diferencia entre ForeignKey y OneToOneField?
    marca = models.ForeignKey(
        Marca, on_delete=models.SET_NULL, null=True, related_name="detalles"
    )
    color = models.CharField(max_length=50, blank=True, null=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        db_table = "detalle_producto"

    def __str__(self):
        return f"{self.producto.nombre} ({self.marca.nombre if self.marca else 'Sin Marca'})"


class ImagenProducto(models.Model):
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, related_name="imagenes"
    )
    url = models.ImageField(upload_to="productos/")
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        db_table = "imagen_producto"

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"


class Campania(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    esta_activo = models.BooleanField(default=True)

    class Meta:
        db_table = "campania"

    def __str__(self):
        return f"{self.nombre} ({self.fecha_inicio} - {self.fecha_fin})"


class Descuento(models.Model):
    TIPO_CHOICES = [
        ("PORCENTAJE", "Porcentaje"),
        ("MONTO", "Monto Fijo"),
    ]
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    monto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    porcentaje = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

    esta_activo = models.BooleanField(default=True)
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, related_name="descuentos"
    )
    sucursal = models.ForeignKey(
        "sucursales.Sucursal", on_delete=models.CASCADE, related_name="descuentos"
    )
    campania = models.ForeignKey(
        Campania,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="descuentos",
    )

    class Meta:
        db_table = "descuento"

    def __str__(self):
        return f"{self.nombre} - {self.tipo}"
