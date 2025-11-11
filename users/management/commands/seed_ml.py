import random
import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from tenants.models import Empresa
from products.models import Producto, Categoria 
from users.models import User, Role
from sucursales.models import Sucursal
from ventas.models import Venta, DetalleVenta, Pago, Metodo_pago

# --- Configuración ---
TOTAL_VENTAS_A_CREAR = 500
PORCENTAJE_COMBOS = 0.3 
DIAS_HISTORICOS = 365

# --- Constantes para los patrones (MODIFICADO) ---
# (Asegúrate que estos nombres coincidan con tu 'seed_products.py')
CAT_LAPTOPS = "Laptops"
CAT_ACCESORIOS = "Accesorios"
CAT_DISPOSITIVOS_MOVILES = "Dispositivos Móviles" # <-- MODIFICADO
CAT_AUDIO = "Audio"
SUB_AURICULARES = "Auriculares" # <-- Esto sigue igual (Subcategoría de Audio)


class Command(BaseCommand):
    help = f"🌱 Crea {TOTAL_VENTAS_A_CREAR} ventas (con patrones) para ML."

    def _crear_detalle(self, empresa, venta, producto, total_calculado):
        """Helper para crear un detalle de venta y sumar al total."""
        cantidad = random.choices([1, 2], weights=[0.9, 0.1], k=1)[0]
        precio = producto.precio_venta
        subtotal = cantidad * precio
        
        DetalleVenta.objects.create(
            empresa=empresa,
            venta=venta,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=precio,
            subtotal=subtotal
        )
        return total_calculado + subtotal

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.HTTP_INFO(f"📈 Iniciando seeder de {TOTAL_VENTAS_A_CREAR} ventas para ML..."))

        empresas = Empresa.objects.all()
        if not empresas.exists():
            self.stdout.write(self.style.ERROR("❌ No se encontraron empresas. No se puede continuar."))
            return

        for empresa in empresas:
            self.stdout.write(f"\n🏢 Procesando empresa: {empresa.nombre}")

            # --- 1. Obtener datos base ---
            sucursales = list(Sucursal.objects.filter(empresa=empresa, esta_activo=True))
            metodos_pago = list(Metodo_pago.objects.filter(empresa=empresa, esta_activo=True))
            
            # --- 2. Diferenciar Agentes y Clientes ---
            agentes = list(User.objects.filter(empresa=empresa, is_active=True, role__name="SALES_AGENT"))
            clientes = list(User.objects.filter(empresa=empresa, is_active=True, role__name="CUSTOMER"))

            # --- 3. Obtener productos agrupados por categoría (MODIFICADO) ---
            try:
                productos_laptops = list(Producto.objects.filter(empresa=empresa, subcategoria__categoria__nombre=CAT_LAPTOPS))
                productos_accesorios = list(Producto.objects.filter(empresa=empresa, subcategoria__categoria__nombre=CAT_ACCESORIOS))
                # MODIFICADO: Buscamos la nueva categoría
                productos_dispositivos = list(Producto.objects.filter(empresa=empresa, subcategoria__categoria__nombre=CAT_DISPOSITIVOS_MOVILES))
                productos_auriculares = list(Producto.objects.filter(empresa=empresa, subcategoria__categoria__nombre=CAT_AUDIO, subcategoria__nombre=SUB_AURICULARES))
                
                productos_normales = list(Producto.objects.filter(empresa=empresa).exclude(
                    id__in=[p.id for p in productos_laptops] + 
                           [p.id for p in productos_accesorios] + 
                           [p.id for p in productos_dispositivos] + # <-- MODIFICADO
                           [p.id for p in productos_auriculares]
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Error al filtrar productos por categoría. ¿Ejecutaste 'seed_products' actualizado? Error: {e}"))
                continue

            # --- 4. Validar que tenemos datos para trabajar ---
            productos_todos = list(Producto.objects.filter(empresa=empresa))
            if not all([productos_todos, sucursales, metodos_pago]):
                self.stdout.write(self.style.WARNING(f"  ⚠️ Faltan datos (Productos, Sucursales o Métodos de Pago) para '{empresa.nombre}'. Saltando."))
                continue
            
            if not agentes or not clientes:
                self.stdout.write(self.style.WARNING(f"  ⚠️ No se encontraron 'Agentes' o 'Clientes'. Asignando al azar."))
                agentes = list(User.objects.filter(empresa=empresa, is_active=True))
                clientes = agentes
            
            if not agentes:
                self.stdout.write(self.style.ERROR(f"  ❌ No hay ningún usuario activo para '{empresa.nombre}'. Saltando."))
                continue

            # Validar si podemos crear patrones (MODIFICADO)
            patron_laptop_posible = bool(productos_laptops and productos_accesorios)
            patron_movil_posible = bool(productos_dispositivos and productos_auriculares) # <-- MODIFICADO
            
            if not (patron_laptop_posible or patron_movil_posible):
                 self.stdout.write(self.style.WARNING(f"  ⚠️ No hay productos para Laptops/Accesorios o Disp.Móviles/Auriculares. Los combos serán aleatorios."))

            if not productos_normales:
                productos_normales = productos_todos 

            # --- 5. Lógica de Tipos de Venta (NUEVO) ---
            num_combos = int(TOTAL_VENTAS_A_CREAR * PORCENTAJE_COMBOS)
            num_normales = TOTAL_VENTAS_A_CREAR - num_combos
            
            tipos_de_venta = ["COMBO"] * num_combos + ["NORMAL"] * num_normales
            random.shuffle(tipos_de_venta) 

            self.stdout.write(f"  ⏳ Creando {num_normales} ventas normales y {num_combos} ventas combo...")

            # --- 6. Iniciar la transacción atómica ---
            try:
                with transaction.atomic():
                    ventas_creadas_count = 0
                    
                    for i, tipo_venta in enumerate(tipos_de_venta):
                        
                        # ... (Lógica de Fecha, Canal, Pago y Venta sin cambios) ...
                        
                        dias_aleatorios = random.randint(1, DIAS_HISTORICOS)
                        fecha_venta = timezone.now() - datetime.timedelta(days=dias_aleatorios)
                        fecha_venta = fecha_venta.replace(hour=random.randint(8, 20), minute=random.randint(0, 59))
                        canal_aleatorio = random.choice(["POS", "WEB"])
                        usuario_aleatorio = random.choice(agentes) if canal_aleatorio == "POS" else random.choice(clientes)
                        sucursal_aleatoria = random.choice(sucursales)
                        metodo_aleatorio = random.choice(metodos_pago)
                        
                        pago = Pago.objects.create(
                            empresa=empresa, metodo=metodo_aleatorio, monto=0, estado="completado",
                            fecha=fecha_venta, referencia=f"PAY-ML-{i+1:04d}"
                        )
                        venta = Venta.objects.create(
                            empresa=empresa, numero_nota=f"NV-ML-{sucursal_aleatoria.id}-{i+1:05d}",
                            usuario=usuario_aleatorio, sucursal=sucursal_aleatoria, pago=pago,
                            fecha=fecha_venta, total=0, estado="Completado", canal=canal_aleatorio
                        )

                        # --- 8. Crear Detalles de Venta (LÓGICA MODIFICADA) ---
                        total_calculado = 0
                        productos_en_esta_venta = []

                        if tipo_venta == "COMBO":
                            # 50/50 chance de qué patrón intentar (si es posible)
                            if patron_laptop_posible and (not patron_movil_posible or random.random() < 0.5):
                                # PATRÓN 1: Laptop + 1 o 2 Accesorios
                                prod1 = random.choice(productos_laptops)
                                productos_en_esta_venta.append(prod1)
                                num_accesorios = random.choices([1, 2], weights=[0.7, 0.3], k=1)[0]
                                if len(productos_accesorios) >= num_accesorios:
                                    accesorios = random.sample(productos_accesorios, num_accesorios)
                                    productos_en_esta_venta.extend(accesorios)
                                
                            elif patron_movil_posible: # <-- MODIFICADO
                                # PATRÓN 2: Dispositivo Móvil + Auriculares
                                prod1 = random.choice(productos_dispositivos) # <-- MODIFICADO
                                prod2 = random.choice(productos_auriculares)
                                productos_en_esta_venta = [prod1, prod2]
                                
                                # 30% chance de añadir un accesorio extra (Case, Cargador)
                                if random.random() < 0.3 and productos_accesorios:
                                    productos_en_esta_venta.append(random.choice(productos_accesorios))
                            
                            else:
                                # Fallback: Combo aleatorio
                                num_detalles = random.randint(2, 3)
                                if len(productos_normales) >= num_detalles:
                                    productos_en_esta_venta = random.sample(productos_normales, num_detalles)

                        
                        if tipo_venta == "NORMAL" or not productos_en_esta_venta:
                            # Venta normal (1 producto) o el combo falló
                            if productos_normales:
                                productos_en_esta_venta = [random.choice(productos_normales)]
                            elif productos_todos:
                                productos_en_esta_venta = [random.choice(productos_todos)]

                        # --- 9. Crear los Detalles basado en la lista ---
                        for producto in set(productos_en_esta_venta): 
                            total_calculado = self._crear_detalle(empresa, venta, producto, total_calculado)

                        # --- 10. Actualizar Venta y Pago ---
                        if total_calculado == 0:
                            if venta.pk: venta.delete()
                            if pago.pk: pago.delete()
                            continue

                        venta.total = total_calculado
                        venta.save()
                        pago.monto = total_calculado
                        pago.save()
                        ventas_creadas_count += 1
                    
                    self.stdout.write(self.style.SUCCESS(f"  ✅ ¡Éxito! Se crearon {ventas_creadas_count} ventas para {empresa.nombre}."))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Error durante la transacción para '{empresa.nombre}': {e}"))
                import traceback
                traceback.print_exc() 

        self.stdout.write(self.style.SUCCESS(f"\n🎉 ¡Proceso completado! Seeder de entrenamiento ML finalizado."))