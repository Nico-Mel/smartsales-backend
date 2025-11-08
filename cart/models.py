from django.db import models

# Create your models here.
class Cart(models.Model):
    empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True)
    usuario = models.ForeignKey('users.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=[
        ('activo', 'Activo'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
        ('inactivo', 'Inactivo'),
    ], default='activo')

    class Meta:
        db_table = 'cart'
    
    def __str__(self):
        return f"Carrito #{self.id} - {self.usuario.email} - {self.estado}"
    
class CartItem(models.Model):
    empresa = models.ForeignKey('tenants.Empresa', on_delete=models.CASCADE, null=True, blank=True)
    cart = models.ForeignKey(Cart, related_name = 'item',on_delete=models.CASCADE)
    producto = models.ForeignKey('products.Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        db_table = 'cart_item'
    def __str__(self):
        return f"Item #{self.id} - {self.producto.nombre} - {self.cantidad}"