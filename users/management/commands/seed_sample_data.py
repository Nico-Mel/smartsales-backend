# users/management/commands/seed_sample_data.py
import random, datetime
from django.core.management.base import BaseCommand
from faker import Faker
from products.models import (
    Categoria, SubCategoria, Marca, Producto,
    DetalleProducto, ImagenProducto
)
from sucursales.models import Departamento, Sucursal, StockSucursal
from tenants.models import Empresa
from users.models import User


class Command(BaseCommand):
    help = "Puebla la BD con datos de ejemplo (productos, categorías, marcas, stock, etc.) para pruebas SaaS."

    def handle(self, *args, **kwargs):
        fake = Faker("es_ES")
        self.stdout.write(self.style.MIGRATE_HEADING("=== 🌱 Iniciando carga de datos de ejemplo ==="))

        # ====== 1️⃣ Empresa base ======
        empresa = Empresa.objects.first()
        if not empresa:
            self.stdout.write(self.style.ERROR("❌ No hay empresa. Ejecuta primero: python manage.py seed_users_data"))
            return

        sucursal = Sucursal.objects.filter(empresa=empresa).first()
        if not sucursal:
            self.stdout.write(self.style.ERROR("❌ No hay sucursal. Ejecuta primero: python manage.py seed_users_data"))
            return

        self.stdout.write(self.style.SUCCESS(f"🏢 Empresa activa: {empresa.nombre}"))
        self.stdout.write(self.style.SUCCESS(f"🏬 Sucursal usada: {sucursal.nombre}"))

        # ====== 2️⃣ Marcas ======
        marcas = ["Samsung", "LG", "Sony", "Oster", "Mabe", "Philips"]
        for m in marcas:
            Marca.objects.get_or_create(
                nombre=m,
                empresa=empresa,
                defaults={
                    "descripcion": f"Fabricante {m}",
                    "pais_origen": random.choice(["China", "Corea del Sur", "Japón", "México"]),
                    "esta_activo": True,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"✅ Marcas aseguradas: {len(marcas)}"))

        # ====== 3️⃣ Categorías y Subcategorías ======
        categorias_data = {
            "ELECTROHOGAR": ["Licuadoras", "Batidoras", "Microondas"],
            "TECNOLOGÍA": ["Televisores", "Computadoras", "Audio"],
        }

        for cat_nombre, sub_list in categorias_data.items():
            categoria, _ = Categoria.objects.get_or_create(nombre=cat_nombre, empresa=empresa)
            for sub_nombre in sub_list:
                SubCategoria.objects.get_or_create(
                    nombre=sub_nombre,
                    empresa=empresa,
                    categoria=categoria,
                )
        self.stdout.write(self.style.SUCCESS("✅ Categorías y subcategorías creadas."))

        # ====== 4️⃣ Productos ======
        subcategorias = list(SubCategoria.objects.filter(empresa=empresa))
        marcas_obj = list(Marca.objects.filter(empresa=empresa))

        for i in range(10):
            sub = random.choice(subcategorias)
            marca = random.choice(marcas_obj)
            producto, created = Producto.objects.get_or_create(
                nombre=f"{sub.nombre} {marca.nombre} {i+1}",
                empresa=empresa,
                defaults={
                    "precio_venta": round(random.uniform(500, 2500), 2),
                    "descripcion": fake.text(max_nb_chars=120),
                    "marca": marca,
                    "subcategoria": sub,
                    "esta_activo": True,
                },
            )

            # Crear detalle técnico (solo si es nuevo)
            if created:
                DetalleProducto.objects.get_or_create(
                    producto=producto,
                    empresa=empresa,
                    defaults={
                        "potencia": f"{random.randint(800, 2500)}W",
                        "voltaje": random.choice(["110V", "220V"]),
                        "velocidades": str(random.randint(1, 5)),
                        "tecnologias": random.choice(["Inverter", "Eco", "Smart", "Turbo"]),
                    },
                )

                # Crear una imagen de muestra
                ImagenProducto.objects.get_or_create(
                    producto=producto,
                    empresa=empresa,
                    defaults={
                        "url": f"https://placehold.co/400x300?text={producto.nombre.replace(' ', '+')}",
                        "descripcion": f"Imagen de {producto.nombre}",
                    },
                )

                # Crear stock por sucursal
                StockSucursal.objects.get_or_create(
                    producto=producto,
                    sucursal=sucursal,
                    defaults={"stock": random.randint(5, 20)},
                )

        self.stdout.write(self.style.SUCCESS("🎯 Productos, detalles, imágenes y stock generados correctamente."))

        # ====== 5️⃣ Clientes de prueba ======
        for i in range(5):
            email = f"cliente{i+1}@demo.com"
            User.objects.get_or_create(
                email=email,
                defaults={
                    "nombre": fake.first_name(),
                    "apellido": fake.last_name(),
                    "telefono": fake.phone_number()[:15],
                    "password": "pbkdf2_sha256$...",
                    "empresa": empresa,
                },
            )
        self.stdout.write(self.style.SUCCESS("👥 Clientes de prueba asegurados."))

        # ====== ✅ Final ======
        self.stdout.write(self.style.SUCCESS("\n🎉 Datos de muestra generados exitosamente."))
