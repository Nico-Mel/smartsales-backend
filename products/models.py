# products/models.py
from django.db import models

class Marca(models.Model):
    #Representa al fabricante del producto (Ej: Samsung, LG, Sony).
    empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True, related_name='marcas')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    pais_origen = models.CharField(max_length=100, blank=True, null=True)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        db_table = "marca"
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        unique_together = ("empresa", "nombre")
    def __str__(self):
        return self.nombre


class Categoria(models.Model): #(Nivel 1)
    #Categoría principal o de Nivel 1 (Ej: "ELECTROHOGAR", "LÍNEA BLANCA")
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    esta_activo = models.BooleanField(default=True)
    empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True, related_name='categorias')
    class Meta:
        db_table = "categoria"
        verbose_name = "Categoría (Nivel 1)"
        verbose_name_plural = "Categorías (Nivel 1)"
        unique_together = ("empresa", "nombre")

    def __str__(self):
        return self.nombre


class SubCategoria(models.Model): #Nivel 2
    #Subcategoría o Nivel 2 (Ej: "Licuadoras", "Batidoras").
    # Enlace al padre (Nivel 1)
    empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True,related_name='subcategorias_empresa' )
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.CASCADE, 
        related_name="subcategorias"
    )
    
    nombre = models.CharField(max_length=100)    
    descripcion = models.TextField(blank=True, null=True)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        db_table = "subcategoria" # Nuevo nombre de tabla
        verbose_name = "Subcategoría (Nivel 2)"
        verbose_name_plural = "Subcategorías (Nivel 2)"
        ordering = ['categoria__nombre', 'nombre']
        unique_together = ("empresa", "nombre")

    def __str__(self):
        # Muestra "ELECTROHOGAR > Licuadoras"
        return f"{self.categoria.nombre} > {self.nombre}"

class Producto(models.Model):
    """
    El Producto principal. Este es el "SKU".
    Aquí va el precio, el stock y la info de venta.
    """
    empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, related_name='productos', null=True, blank=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True, 
                                   help_text="El párrafo de marketing (Información Adicional)")
    
    # <-- NUEVO: El SKU, identificador único de negocio
    sku = models.CharField(max_length=100, blank=True, null=True, 
                           help_text="Código único de producto (SKU) para gestión e inventario")

    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    marca = models.ForeignKey(
        Marca,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos"
    )
    
    subcategoria = models.ForeignKey(
        SubCategoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    esta_activo = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        """
        Genera automáticamente un SKU único por empresa si no existe.
        """
        if not self.sku:
            prefix = f"SKU-{self.empresa.id if self.empresa else 'GEN'}"
            last = Producto.objects.filter(empresa=self.empresa).order_by('id').last()
            next_num = 1 if not last else last.id + 1
            self.sku = f"{prefix}-{next_num:05d}"
        super().save(*args, **kwargs)

    class Meta:
        db_table = "producto"
        verbose_name = "Producto (SKU)"
        verbose_name_plural = "Productos (SKUs)"
        unique_together = ("empresa", "sku") 

    def __str__(self):
        return f"{self.nombre} ({self.sku or 'Sin SKU'})"

class DetalleProducto(models.Model): 
    """
    La "Ficha Técnica" (Características) del producto.
    Es un anexo con datos extra.
    """
    # Relación Uno-a-Uno. Un producto tiene UNA ficha técnica.
    producto = models.OneToOneField(
        Producto, on_delete=models.CASCADE, related_name="detalle"
    )
    empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True, related_name='detalles_producto')
    
    #Campos de ejemplo para la ficha técnica
    potencia = models.CharField(max_length=100, blank=True, null=True)
    velocidades = models.CharField(max_length=100, blank=True, null=True)
    voltaje = models.CharField(max_length=100, blank=True, null=True)
    aire_frio = models.CharField(max_length=100, blank=True, null=True)
    tecnologias = models.CharField(max_length=255, blank=True, null=True)
    largo_cable = models.CharField(max_length=100, blank=True, null=True)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        db_table = "detalle_producto"
        verbose_name = "Ficha Técnica (Detalle)"
        verbose_name_plural = "Fichas Técnicas (Detalles)"

    def __str__(self):
        return f"Ficha técnica de {self.producto.nombre}"
    
# class ProductoCategoria(models.Model):
#     producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
#     categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
#     esta_activo = models.BooleanField(default=True)
#     empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True)
#     class Meta:
#         db_table = "producto_categoria"
#         unique_together = ("producto", "categoria")

#     def __str__(self):
#         return f"{self.producto.nombre}-{self.categoria.nombre}"


# class DetalleProducto(models.Model):
#     producto = models.OneToOneField(
#         Producto, on_delete=models.CASCADE, related_name="detalle"
#     )
#     # cual es la diferencia entre ForeignKey y OneToOneField?
#     marca = models.ForeignKey(
#         Marca, on_delete=models.SET_NULL, null=True, related_name="detalles"
#     )
#     empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True)
#     color = models.CharField(max_length=50, blank=True, null=True)
#     precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     esta_activo = models.BooleanField(default=True)

#     class Meta:
#         db_table = "detalle_producto"
#         verbose_name = "Ficha Técnica (Detalle)"
#         verbose_name_plural = "Fichas Técnicas (Detalles)"

#     def __str__(self):
#         return f"Ficha técnica de {self.producto.nombre}"


class ImagenProducto(models.Model):

    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, related_name="imagenes"
    )
    empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True, related_name='imagenes_producto')
    url = models.ImageField(upload_to="productos/")
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        db_table = "imagen_producto"
        verbose_name = "Imagen de Producto"
        verbose_name_plural = "Imágenes de Producto"

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"


class Campania(models.Model):
    empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True, related_name='campanias')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    esta_activo = models.BooleanField(default=True)

    class Meta:
        db_table = "campania"
        verbose_name = "Campaña"
        verbose_name_plural = "Campañas"
        unique_together = ("empresa", "nombre")

    def __str__(self):
        return f"{self.nombre} ({self.fecha_inicio} - {self.fecha_fin})"

class Descuento(models.Model):
    empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True, related_name='descuentos')
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
        verbose_name = "Descuento"
        verbose_name_plural = "Descuentos"
        unique_together = ("empresa", "producto", "sucursal")

    def __str__(self):
        return f"{self.nombre} - {self.tipo}"