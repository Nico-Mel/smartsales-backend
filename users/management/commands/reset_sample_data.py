from django.core.management.base import BaseCommand
from django.db.models import Q

# Importa los modelos de sus respectivas apps
from products.models import (
    Categoria, SubCategoria, Marca, Producto, 
    DetalleProducto, ImagenProducto, Descuento, Campania
)
from sucursales.models import Departamento, Direccion, Sucursal, StockSucursal
from users.models import User

class Command(BaseCommand):
    help = 'Resetea los datos de muestra (Productos, Clientes, etc.)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando reseteo de datos de muestra...'))

        # El orden de borrado es importante para evitar errores de ForeignKey
        
        # 1. Borrar Stock y Descuentos
        count, _ = StockSucursal.objects.all().delete()
        self.stdout.write(f'StockSucursal eliminados: {count}')
        count, _ = Descuento.objects.all().delete()
        self.stdout.write(f'Descuentos eliminados: {count}')

        # 2. Borrar Detalles e Imágenes
        count, _ = ImagenProducto.objects.all().delete()
        self.stdout.write(f'ImagenProducto eliminados: {count}')
        count, _ = DetalleProducto.objects.all().delete()
        self.stdout.write(f'DetalleProducto eliminados: {count}')

        # 3. Borrar Productos
        count, _ = Producto.objects.all().delete()
        self.stdout.write(f'Productos eliminados: {count}')
        
        # 4. Borrar SubCategorías y Categorías
        count, _ = SubCategoria.objects.all().delete()
        self.stdout.write(f'SubCategorias eliminadas: {count}')
        count, _ = Categoria.objects.all().delete()
        self.stdout.write(f'Categorias eliminadas: {count}')

        # 5. Borrar Marcas y Campañas
        count, _ = Marca.objects.all().delete()
        self.stdout.write(f'Marcas eliminadas: {count}')
        count, _ = Campania.objects.all().delete()
        self.stdout.write(f'Campanias eliminadas: {count}')

        # 6. Borrar Clientes (Usuarios no-admin)
        count, _ = User.objects.filter(is_staff=False, is_superuser=False).delete()
        self.stdout.write(f'Clientes (Usuarios no-staff) eliminados: {count}')

        # 7. Borrar Sucursales y Direcciones (Excepto la Central)
        try:
            central = Sucursal.objects.get(nombre='Sucursal Central')
            # Borrar todas las direcciones que NO sean de la sucursal central
            count, _ = Direccion.objects.exclude(id=central.direccion.id).delete()
            self.stdout.write(f'Direcciones (no-central) eliminadas: {count}')
            
            # Borrar todas las sucursales que NO sean la central
            count, _ = Sucursal.objects.exclude(id=central.id).delete()
            self.stdout.write(f'Sucursales (no-central) eliminadas: {count}')
            
            # Borrar todos los departamentos que no estén en uso por la dirección central
            count, _ = Departamento.objects.exclude(direccion__id=central.direccion.id).delete()
            self.stdout.write(f'Departamentos (no-central) eliminados: {count}')

        except Sucursal.DoesNotExist:
            self.stdout.write(self.style.WARNING('No se encontró Sucursal Central, omitiendo limpieza de sucursales/direcciones.'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Omitiendo limpieza de direcciones/sucursales: {e}'))

        self.stdout.write(self.style.SUCCESS('\nReseteo de datos de muestra completo.'))