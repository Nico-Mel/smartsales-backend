import random, datetime
from django.core.management.base import BaseCommand
from faker import Faker
from tenants.models import Empresa
from products.models import (
    Marca, Categoria, SubCategoria, Producto, DetalleProducto,
    ImagenProducto, Campania, Descuento
)
from ventas.models import Metodo_pago
from shipping.models import Agencia
from sucursales.models import Sucursal, StockSucursal

# --- 1. Definición centralizada de datos (NUEVO) ---

# Marcas y sus prefijos para SKU
MARCAS_DATA = {
    # Dispositivos Móviles, TVs, Audio
    "Samsung": "SAM", "LG": "LG", "Sony": "SON", "Xiaomi": "XIA", "Apple": "APP",
    # Laptops y Accesorios
    "HP": "HP", "Dell": "DEL", "Logitech": "LOG", "Razer": "RAZ",
    # Electrohogar
    "Oster": "OST", "Mabe": "MAB", "Philips": "PHI",
    # Audio
    "JBL": "JBL", "Bose": "BOS"
}

# Categorías, Subcategorías y sus prefijos para SKU
CATEGORIAS_DATA = {
    # MODIFICADO: "Celulares" ahora es "Dispositivos Móviles"
    "Dispositivos Móviles": {"prefix": "DIS", "subs": ["Smartphones", "Tablets", "Celulares Básicos"]},
    "Laptops":               {"prefix": "LAP", "subs": ["Notebooks", "Ultrabooks", "Gaming Laptops"]},
    "Accesorios":            {"prefix": "ACC", "subs": ["Mouses", "Teclados", "Cases", "Cargadores"]},
    "Audio":                 {"prefix": "AUD", "subs": ["Auriculares", "Parlantes Bluetooth"]},
    "Televisores":           {"prefix": "TEL", "subs": ["Smart TV", "OLED", "QLED"]},
    "Electrohogar":          {"prefix": "ELE", "subs": ["Licuadoras", "Batidoras", "Microondas"]},
}

# Lógica de asociación: Qué marcas venden qué categorías (NUEVO)
LOGICA_PRODUCTOS = {
    "Dispositivos Móviles": ["Samsung", "Xiaomi", "Apple", "LG"],
    "Laptops": ["HP", "Dell", "Apple", "Razer", "Samsung"],
    "Accesorios": ["Logitech", "Razer", "HP", "Dell", "Apple", "Samsung"],
    "Audio": ["Sony", "JBL", "Bose", "Xiaomi", "Apple", "Samsung"],
    "Televisores": ["LG", "Samsung", "Sony", "Philips"],
    "Electrohogar": ["Oster", "Mabe", "Philips", "LG", "Samsung"],
}

# --- Fin de la definición de datos ---


class Command(BaseCommand):
    help = "🌱 Pobla la app products con datos de ejemplo LÓGICOS para cada empresa"

    def handle(self, *args, **kwargs):
        fake = Faker("es_ES")
        empresas = Empresa.objects.all()
        if not empresas.exists():
            self.stdout.write(self.style.ERROR("❌ No hay empresas. Ejecuta primero: python manage.py seed_users_data"))
            return

        for empresa in empresas:
            self.stdout.write(self.style.HTTP_INFO(f"\n🏢 Poblando datos para empresa: {empresa.nombre}"))
            
            # Contadores para SKUs únicos por empresa
            product_counter = 1
            
            # --- 1. Marcas (MODIFICADO) ---
            # Crea las marcas desde nuestra data centralizada
            marcas_creadas = {} # Diccionario para rápido acceso
            for nombre_marca in MARCAS_DATA.keys():
                obj, _ = Marca.objects.get_or_create(nombre=nombre_marca, empresa=empresa, defaults={"esta_activo": True})
                marcas_creadas[nombre_marca] = obj
            self.stdout.write(f"  ✓ Marcas creadas/verificadas ({len(marcas_creadas)})")

            # --- 2. Categorías y Subcategorías (MODIFICADO) ---
            subcategorias_creadas = {} # Diccionario para rápido acceso
            for cat_nombre, data in CATEGORIAS_DATA.items():
                c, _ = Categoria.objects.get_or_create(nombre=cat_nombre, empresa=empresa)
                for sub_nombre in data["subs"]:
                    s, _ = SubCategoria.objects.get_or_create(nombre=sub_nombre, categoria=c, empresa=empresa)
                    subcategorias_creadas[sub_nombre] = s
            self.stdout.write(f"  ✓ Categorías y Subcategorías creadas/verificadas")

            # --- 3. Campañas (MODIFICADO: 2 campañas más) ---
            hoy = datetime.date.today()
            campanias = [
                {"nombre": "Campaña Verano", "desc": "Ofertas de verano", "inicio": hoy, "fin": hoy + datetime.timedelta(days=30)},
                {"nombre": "Cyber Monday", "desc": "Descuentos Tech", "inicio": hoy + datetime.timedelta(days=40), "fin": hoy + datetime.timedelta(days=47)},
                {"nombre": "Navidad 2025", "desc": "Especiales de Navidad", "inicio": hoy + datetime.timedelta(days=60), "fin": hoy + datetime.timedelta(days=90)},
            ]
            for c in campanias:
                Campania.objects.get_or_create(
                    nombre=c["nombre"],
                    empresa=empresa,
                    defaults={
                        "descripcion": c["desc"],
                        "fecha_inicio": c["inicio"],
                        "fecha_fin": c["fin"],
                    },
                )
            self.stdout.write(f"  ✓ Campañas creadas/verificadas ({len(campanias)})")

            # --- 4. Métodos de Pago y Agencias (Sin cambios) ---
            metodos_pago = [
                {"nombre": "Efectivo", "descripcion": "Pago en efectivo", "proveedor": "Sistema"},
                {"nombre": "Tarjeta Crédito", "descripcion": "Pago con tarjeta", "proveedor": "Visa/Mastercard"},
                {"nombre": "Stripe", "descripcion": "Pago vía Stripe", "proveedor": "Stripe"},
            ]
            for mp in metodos_pago:
                Metodo_pago.objects.get_or_create(nombre=mp["nombre"], empresa=empresa, defaults={**mp, "esta_activo": True})
            
            agencias = [
                {"nombre": "DHL Express", "contacto": "Juan Pérez", "telefono": "800-1234"},
                {"nombre": "Correo Bolivia", "contacto": "María López", "telefono": "800-9012"},
            ]
            for ag in agencias:
                Agencia.objects.get_or_create(nombre=ag["nombre"], empresa=empresa, defaults={**ag, "esta_activo": True})
            
            # --- 5. Productos y Stock (LÓGICA COMPLETAMENTE NUEVA) ---
            self.stdout.write("  ⏳ Generando productos con lógica de marcas y SKUs...")
            sucursales = Sucursal.objects.filter(empresa=empresa)
            productos_creados_count = 0

            # Iteramos sobre la LÓGICA definida
            for cat_nombre, marcas_permitidas in LOGICA_PRODUCTOS.items():
                
                cat_data = CATEGORIAS_DATA[cat_nombre]
                cat_sku_prefix = cat_data["prefix"]
                subcategorias_de_esta_cat = [subcategorias_creadas[s] for s in cat_data["subs"]]

                if not subcategorias_de_esta_cat:
                    continue

                # Para cada marca permitida en esta categoría...
                for marca_nombre in marcas_permitidas:
                    marca_obj = marcas_creadas[marca_nombre]
                    marca_sku_prefix = MARCAS_DATA[marca_nombre]
                    
                    # Creamos 2 o 3 productos de ejemplo para esta combinación
                    for _ in range(random.randint(2, 3)):
                        sub_obj = random.choice(subcategorias_de_esta_cat)
                        
                        # Generar SKU (MODIFICADO)
                        sku_num = f"{product_counter:04d}" # Ej: 0001, 0002
                        sku_final = f"{cat_sku_prefix}-{marca_sku_prefix}-{sku_num}" # Ej: DIS-SAM-0001
                        product_counter += 1
                        
                        nombre_producto = f"{sub_obj.nombre} {marca_obj.nombre} {fake.word().capitalize()}"
                        
                        # Usamos SKU como clave única, es más robusto
                        p, created = Producto.objects.get_or_create(
                            sku=sku_final,
                            empresa=empresa,
                            defaults={
                                "nombre": nombre_producto,
                                "precio_venta": round(random.uniform(50, 3000), 2),
                                "marca": marca_obj,
                                "subcategoria": sub_obj,
                            },
                        )
                        
                        if not created: # Si el SKU ya existía, saltamos
                            continue 
                            
                        productos_creados_count += 1

                        DetalleProducto.objects.get_or_create(
                            producto=p,
                            empresa=empresa,
                            defaults={"potencia": "200W", "voltaje": "220V"},
                        )
                        ImagenProducto.objects.get_or_create(
                            producto=p,
                            empresa=empresa,
                            defaults={"url": f"https://placehold.co/400x300?text={p.sku.replace(' ', '+')}"}, # Usar SKU en placeholder
                        )
                        
                        # Stock para CADA sucursal
                        for sucursal in sucursales:
                            stock_final = random.randint(20, 100)
                            StockSucursal.objects.get_or_create(
                                producto=p,
                                sucursal=sucursal,
                                empresa=empresa,
                                defaults={"stock": stock_final},
                            )

            self.stdout.write(f"  ✓ {productos_creados_count} productos lógicos creados.")

            # --- 6. Descuentos (Sin cambios) ---
            productos = list(Producto.objects.filter(empresa=empresa))
            if productos and sucursales.exists():
                suc_choice = random.choice(sucursales)
                for p in random.sample(productos, min(5, len(productos))):
                    Descuento.objects.get_or_create(
                        nombre=f"Descuento {p.nombre}",
                        tipo="PORCENTAJE",
                        porcentaje=random.randint(5, 15),
                        producto=p,
                        sucursal=suc_choice, 
                        empresa=empresa,
                        defaults={"esta_activo": True},
                    )

            self.stdout.write(self.style.SUCCESS(f"✅ Datos creados para empresa {empresa.nombre}"))
        self.stdout.write(self.style.SUCCESS("\n🎯 Seed de products LÓGICO completado ✅"))