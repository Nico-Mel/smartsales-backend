from django.db import models

class Metodo_pago(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    proveedor = models.TextField(blank=True, null = True)# stripe, qr, paypal

    class Meta:
        db_name ='metodo_pago'
    def __str__(self):
        return self.nombre
    
class Pago(models.Model):
    metodo = models.ForeignKey(Metodo_pago, on_delete=models.SET_NULL, null = True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('completado','Completado'),
        ('fallido','Fallido'),
    ])
    fecha = models.DateTimeField(auto_now=True)
    referencia = models.CharField(max_length=250, blank=True, null = True)
    class Meta: 
        db_name = 'pago'
    def __str__(self):
        return f"{self.metodo.nombre} - {self.monto} - {self.estado}"



# Create your models here.
class Venta(models.Model):

    usuario = models.ForeignKey('users.User',on_delete=models.CASCADE)
    pago = models.OneToOneField(Pago, on_delete=models.SET_NULL, null = True, blank=True)
    fecha= models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=50, choices =[
        ('pendiente', 'Pendiente'),
        ('procesando','Procesando'),
        ('enviado','Enviado'),
        ('entregado','Entregado'),
        ('cancelado','Cancelado')
    ])

    class Meta:
        db_table = 'venta'
    def __str__(self):
        return f"Venta #{self.id} - {self.usuario.email} - {self.total} - {self.estado}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name = 'detalles')
    producto = models.ForeignKey('products.Producto',on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
