import random
import datetime
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from faker import Faker

# Importa los modelos de sus respectivas apps
from products.models import (
    Categoria, SubCategoria, Marca, Producto, 
    DetalleProducto, ImagenProducto, Descuento, Campania
)
from sucursales.models import Departamento, Direccion, Sucursal, StockSucursal
from users.models import User, Role

class Command(BaseCommand):
    help = 'Seeder: Pobla la BD con datos de muestra (retail electrodomésticos)'

    def handle(self, *args, **kwargs):
        fake = Faker('es_ES')  # Generador de datos falsos en español
        self.stdout.write(self.style.SUCCESS('Iniciando seeder de datos de muestra...'))

        # --- 0. OBTENER DATOS BASE (de seed-config) ---
        try:
            role_customer = Role.objects.get(name='CUSTOMER')
            sucursal_central = Sucursal.objects.get(nombre='Sucursal Central')
        except Role.DoesNotExist:
            self.stdout.write(self.style.ERROR('ERROR: Rol "CUSTOMER" no encontrado. Ejecuta "seed-config" primero.'))
            return
        except Sucursal.DoesNotExist:
            self.stdout.write(self.style.ERROR('ERROR: "Sucursal Central" no encontrada. Ejecuta "seed-config" primero.'))
            return
        
        sucursales_list = [sucursal_central]

        # --- 1. DEPARTAMENTOS ---
        departamentos_nombres = ['Santa Cruz', 'La Paz', 'Cochabamba']
        departamentos_obj = []
        for nombre in departamentos_nombres:
            dep, _ = Departamento.objects.get_or_create(nombre=nombre)
            departamentos_obj.append(dep)
        self.stdout.write(f'Departamentos asegurados: {len(departamentos_obj)}')

        # --- 2. CLIENTES (User) ---
        clientes_obj = []
        for i in range(10):
            email = f'cliente{i+1}@ejemplo.com'
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email,
                    password='password123',
                    nombre=fake.first_name(),
                    apellido=fake.last_name(),
                    telefono=fake.phone_number()[:15],
                    role=role_customer
                )
                clientes_obj.append(user)
        self.stdout.write(f'Clientes creados: {len(clientes_obj)}')
        if not clientes_obj:
            clientes_obj = list(User.objects.filter(role=role_customer))

        # --- 3. DIRECCIONES (Clientes y Sucursales) ---
        # Crear direcciones para clientes
        for cliente in clientes_obj:
            Direccion.objects.get_or_create(
                cliente=cliente,
                defaults={
                    'departamento': random.choice(departamentos_obj),
                    'pais': 'Bolivia',
                    'ciudad': random.choice(departamentos_nombres),
                    'zona': fake.street_name(),
                    'calle': fake.street_address(),
                    'numero': fake.building_number(),
                    'referencia': 'Casa color ' + fake.color_name(),
                }
            )
        self.stdout.write(f'Direcciones de clientes creadas.')

        # Crear 2 sucursales adicionales
        suc_norte_dir, _ = Direccion.objects.get_or_create(
            calle='Av. Banzer', numero='km 5', zona='Norte', ciudad='Santa Cruz', pais='Bolivia',
            defaults={'departamento': departamentos_obj[0]}
        )
        suc_norte, _ = Sucursal.objects.get_or_create(nombre='Sucursal Norte', defaults={'direccion': suc_norte_dir})
        
        suc_sur_dir, _ = Direccion.objects.get_or_create(
            calle='Av. Santos Dumont', numero='4to Anillo', zona='Sur', ciudad='Santa Cruz', pais='Bolivia',
            defaults={'departamento': departamentos_obj[0]}
        )
        suc_sur, _ = Sucursal.objects.get_or_create(nombre='Sucursal Sur', defaults={'direccion': suc_sur_dir})
        
        sucursales_list.extend([suc_norte, suc_sur])
        self.stdout.write(f'Sucursales adicionales creadas. Total: {len(sucursales_list)}')

        # --- 4. CAMPAÑAS ---
        today = datetime.date.today()
        campania_navidad, _ = Campania.objects.get_or_create(
            nombre='Campaña Navidad',
            defaults={
                'descripcion': 'Descuentos de fin de año.',
                'fecha_inicio': today,
                'fecha_fin': today + datetime.timedelta(days=30)
            }
        )
        campania_cyber, _ = Campania.objects.get_or_create(
            nombre='CyberMonday',
            defaults={
                'descripcion': 'Ofertas de tecnología.',
                'fecha_inicio': today - datetime.timedelta(days=10),
                'fecha_fin': today - datetime.timedelta(days=5),
                'esta_activo': False
            }
        )
        self.stdout.write('Campañas creadas.')

        # --- 5. MARCAS ---
        marcas_nombres = ['Sony', 'Samsung', 'LG', 'Oster', 'Mabe', 'Indurama', 'HP', 'Logitech', 'Gama', 'Philips']
        marcas_obj = []
        for nombre in marcas_nombres:
            marca, _ = Marca.objects.get_or_create(nombre=nombre)
            marcas_obj.append(marca)
        self.stdout.write(f'Marcas creadas: {len(marcas_obj)}')

        # --- 6. CATEGORÍAS Y SUBCATEGORÍAS ---
        categorias_data = {
            'LÍNEA BLANCA': ['COCINAS', 'REFRIGERACIÓN', 'LAVADORAS Y SECADORAS', 'HORNOS'],
            'CUIDADO PERSONAL': ['SECADORAS DE CABELLO', 'AFEITADORAS', 'ALISADORAS'],
            'ELECTROHOGAR': ['LICUADORAS', 'MICROONDAS', 'ASPIRADORAS'],
            'TECNOLOGÍA': ['TELEVISORES', 'COMPUTADORAS', 'AUDIO', 'CELULARES'],
            'ZONA GAMER': ['CONSOLAS', 'SILLAS GAMER', 'MONITORES GAMER'],
            'CLIMATIZACIÓN': ['AIRES ACONDICIONADOS', 'VENTILADORES'],
        }
        
        subcategorias_obj = []
        for cat_nombre, sub_list in categorias_data.items():
            cat, _ = Categoria.objects.get_or_create(nombre=cat_nombre)
            for sub_nombre in sub_list:
                sub, _ = SubCategoria.objects.get_or_create(nombre=sub_nombre, defaults={'categoria': cat})
                subcategorias_obj.append(sub)
        self.stdout.write(f'Categorías y Subcategorías creadas.')

        # --- 7. PRODUCTOS ---
        productos_obj = []
        for i in range(15): # Crear 15 productos
            subcat = random.choice(subcategorias_obj)
            marca = random.choice(marcas_obj)
            nombre_prod = f'{subcat.nombre} {marca.nombre} {fake.ean(8)}'
            
            try:
                prod, created = Producto.objects.get_or_create(
                    nombre=nombre_prod,
                    defaults={
                        'sku': fake.bban(),
                        'precio_venta': round(random.uniform(500.0, 7000.0), 2),
                        'descripcion': fake.text(max_nb_chars=150),
                        'marca': marca,
                        'subcategoria': subcat,
                    }
                )
                if created:
                    productos_obj.append(prod)
            except IntegrityError: # En caso de SKU duplicado
                continue
        self.stdout.write(f'Productos creados: {len(productos_obj)}')

        # --- 8. DETALLES, IMÁGENES Y STOCK ---
        for prod in productos_obj:
            # Crear 1 Detalle (si es secadora, por ejemplo)
            if 'SECADORAS' in prod.subcategoria.nombre.upper():
                DetalleProducto.objects.get_or_create(
                    producto=prod,
                    defaults={
                        'potencia': f'{random.randint(1800, 2500)}W',
                        'velocidades': '2',
                        'voltaje': '220V',
                        'aire_frio': 'Sí',
                        'largo_cable': '1.8m'
                    }
                )
            
            # Crear 2 Imágenes placeholder
            for i in range(2):
                ImagenProducto.objects.get_or_create(
                    producto=prod, 
                    descripcion=f'Imagen {i+1} de {prod.nombre}',
                    defaults={'url': f'https://placehold.co/600x400/eeeeee/cccccc?text={prod.nombre.replace(" ", "+")}'}
                )
            
            # Crear Stock en cada Sucursal
            for suc in sucursales_list:
                StockSucursal.objects.get_or_create(
                    producto=prod,
                    sucursal=suc,
                    defaults={'stock': random.randint(5, 50)}
                )
        self.stdout.write(f'Detalles, Imágenes y Stock creados para productos.')

        # --- 9. DESCUENTOS ---
        # Un descuento de porcentaje para Navidad
        Descuento.objects.get_or_create(
            nombre='10% OFF en Lavadoras (Navidad)',
            tipo='PORCENTAJE',
            porcentaje=10.00,
            campania=campania_navidad,
            defaults={'producto': random.choice(productos_obj)} # Opcional: para un producto específico
        )
        # Un descuento de monto fijo
        Descuento.objects.get_or_create(
            nombre='Bs 100 en Televisores',
            tipo='MONTO',
            monto=100.00,
            defaults={'producto': random.choice(productos_obj)}
        )
        self.stdout.write(f'Descuentos creados.')

        self.stdout.write(self.style.SUCCESS('\nSeeder de datos de muestra completo.'))