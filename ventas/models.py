# ventas/models.py
from django.db import models

class Metodo_pago(models.Model):
    empresa = models.ForeignKey(
        'tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True, related_name='metodos_pago'
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    proveedor = models.CharField(max_length=100,blank=True, null = True)# stripe, qr, paypal
    esta_activo = models.BooleanField(default=True)
    class Meta:
        db_table ='metodo_pago'
        unique_together = ('empresa', 'nombre')

    def __str__(self):
        empresa_nombre = getattr(self.empresa, 'nombre', 'Sin empresa')
        return f"{self.nombre} ({empresa_nombre})"
    
class Pago(models.Model):
    empresa = models.ForeignKey(
        'tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True, related_name='pagos'
    )
    metodo = models.ForeignKey(Metodo_pago, on_delete=models.SET_NULL, null = True, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('completado','Completado'),
        ('fallido','Fallido'),
    ],
    default='pendiente')
    fecha = models.DateTimeField()
    referencia = models.CharField(max_length=250, blank=True, null = True)
    class Meta: 
        db_table = 'pago'
        ordering = ['-fecha']
    def __str__(self):
        metodo_nombre = self.metodo.nombre if self.metodo else "Sin método"
        return f"{metodo_nombre} - {self.monto} - {self.estado}"



# Create your models here.
class Venta(models.Model):
    empresa = models.ForeignKey(
        'tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True, related_name='ventas'
    )
    numero_nota = models.CharField(max_length=20, unique = True)

    usuario = models.ForeignKey('users.User',on_delete=models.CASCADE, related_name='ventas')
    sucursal = models.ForeignKey(
        'sucursales.Sucursal', 
        on_delete=models.PROTECT,
        null=True,  # Temporal para la migración
        related_name='ventas'
    )
    CANALES_VENTA = (
        ('POS', 'Punto de Venta'),
        ('WEB', 'Tienda en Línea'),
        ('OTRO', 'Otro'),
    )
    canal = models.CharField(
        max_length=10, 
        choices=CANALES_VENTA, 
        default='POS', # Por defecto es POS, a menos que el frontend diga 'WEB'
        null=True,
        blank=True
    )
    
    pago = models.OneToOneField(Pago, on_delete=models.SET_NULL, null = True, blank=True, related_name='ventas')
    fecha= models.DateTimeField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=50, choices =[
        ('pendiente', 'Pendiente'),
        ('procesando','Procesando'),
        ('enviado','Enviado'),
        ('entregado','Entregado'),
        ('cancelado','Cancelado')
    ], default='pendiente')
    esta_activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'venta'
        ordering = ['-fecha']
        unique_together = ('empresa', 'numero_nota')

    def __str__(self):
        return f"Venta #{self.id} - {self.usuario.email} - {self.total} - {self.estado}"
    
    def save(self, *args, **kwargs):
        if self.numero_nota == 'TEMP-NOTA' or not self.numero_nota:
            last = Venta.objects.filter(empresa=self.empresa).order_by('id').last()
            next_num = 1 if not last else last.id + 1
            self.numero_nota = f"NV-{next_num:05d}"  # ejemplo: NV-00001
        super().save(*args, **kwargs)

class DetalleVenta(models.Model):
    empresa = models.ForeignKey(
        'tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True, related_name='detalles_venta'
    )
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name = 'detalles')
    producto = models.ForeignKey('products.Producto',on_delete=models.CASCADE, related_name='detalles_venta')
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'detalle_venta'
        unique_together = ('empresa', 'venta', 'producto')
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} (${self.subtotal})"
    