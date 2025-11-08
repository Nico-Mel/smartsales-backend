import random, datetime
from django.core.management.base import BaseCommand
from faker import Faker
from tenants.models import Empresa
from products.models import (
    Marca, Categoria, SubCategoria, Producto, DetalleProducto,
    ImagenProducto, Campania, Descuento
)
from sucursales.models import Sucursal, StockSucursal


class Command(BaseCommand):
    help = "🌱 Pobla la app products con datos de ejemplo para cada empresa"

    def handle(self, *args, **kwargs):
        fake = Faker("es_ES")
        empresas = Empresa.objects.all()
        if not empresas.exists():
            self.stdout.write(self.style.ERROR("❌ No hay empresas. Ejecuta primero: python manage.py seed_users_data"))
            return

        for empresa in empresas:
            self.stdout.write(self.style.HTTP_INFO(f"\n🏢 Poblando datos para empresa: {empresa.nombre}"))

            # 1️⃣ Marcas
            marcas = ["Samsung", "LG", "Sony", "Oster", "Mabe", "Philips"]
            for m in marcas:
                Marca.objects.get_or_create(nombre=m, empresa=empresa, defaults={"esta_activo": True})

            # 2️⃣ Categorías y Subcategorías
            categorias = {
                "Electrohogar": ["Licuadoras", "Batidoras", "Microondas"],
                "Tecnología": ["Televisores", "Computadoras", "Audio"],
            }
            for cat, subs in categorias.items():
                c, _ = Categoria.objects.get_or_create(nombre=cat, empresa=empresa)
                for sub in subs:
                    SubCategoria.objects.get_or_create(nombre=sub, categoria=c, empresa=empresa)

            # 3️⃣ Campañas
            hoy = datetime.date.today()
            Campania.objects.get_or_create(
                nombre="Campaña Verano",
                empresa=empresa,
                defaults={
                    "descripcion": "Ofertas de verano",
                    "fecha_inicio": hoy,
                    "fecha_fin": hoy + datetime.timedelta(days=30),
                },
            )

            # 4️⃣ Productos
            subcategorias = list(SubCategoria.objects.filter(empresa=empresa))
            marcas_obj = list(Marca.objects.filter(empresa=empresa))
            sucursal = Sucursal.objects.filter(empresa=empresa).first()

            for i in range(10):
                sub = random.choice(subcategorias)
                marca = random.choice(marcas_obj)
                p, _ = Producto.objects.get_or_create(
                    nombre=f"{sub.nombre} {marca.nombre} {i+1}",
                    empresa=empresa,
                    defaults={
                        "precio_venta": round(random.uniform(400, 2000), 2),
                        "marca": marca,
                        "subcategoria": sub,
                    },
                )
                DetalleProducto.objects.get_or_create(
                    producto=p,
                    empresa=empresa,
                    defaults={"potencia": "2000W", "voltaje": "220V", "velocidades": "3"},
                )
                ImagenProducto.objects.get_or_create(
                    producto=p,
                    empresa=empresa,
                    defaults={"url": f"https://placehold.co/400x300?text={p.nombre.replace(' ', '+')}"},
                )
                StockSucursal.objects.get_or_create(
                    producto=p,
                    sucursal=sucursal,
                    defaults={"stock": random.randint(5, 25)},
                )

            # 5️⃣ Descuentos
            productos = list(Producto.objects.filter(empresa=empresa))
            if productos:
                for p in random.sample(productos, min(3, len(productos))):
                    Descuento.objects.get_or_create(
                        nombre=f"Descuento {p.nombre}",
                        tipo="PORCENTAJE",
                        porcentaje=random.randint(5, 15),
                        producto=p,
                        sucursal=sucursal,
                        empresa=empresa,
                        defaults={"esta_activo": True},
                    )

            self.stdout.write(self.style.SUCCESS(f"✅ Datos creados para empresa {empresa.nombre}"))
        self.stdout.write(self.style.SUCCESS("\n🎯 Seed de products completado ✅"))
