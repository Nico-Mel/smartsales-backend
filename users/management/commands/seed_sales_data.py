import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from tenants.models import Empresa
from users.models import User
from products.models import Producto
from sucursales.models import Sucursal, StockSucursal
from ventas.models import Metodo_pago, Pago, Venta, DetalleVenta
from shipping.models import Agencia, Envio


class Command(BaseCommand):
    help = "🌱 Pobla la app ventas con datos de ejemplo para cada empresa"

    def handle(self, *args, **kwargs):
        empresas = Empresa.objects.all()
        
        for empresa in empresas:
            self.stdout.write(f"🏢 Poblando ventas para: {empresa.nombre}")
            
            # 1️⃣ Métodos de Pago
            metodos_pago = [
                {"nombre": "Efectivo", "descripcion": "Pago en efectivo", "proveedor": "Sistema"},
                {"nombre": "Tarjeta Crédito", "descripcion": "Pago con tarjeta", "proveedor": "Visa/Mastercard"},
                {"nombre": "Transferencia", "descripcion": "Transferencia bancaria", "proveedor": "Bancos"},
                {"nombre": "Stripe", "descripcion": "Pago vía Stripe", "proveedor": "Stripe"},
            ]
            for mp in metodos_pago:
                Metodo_pago.objects.get_or_create(
                    nombre=mp["nombre"],
                    empresa=empresa,
                    defaults={
                        "descripcion": mp["descripcion"],
                        "proveedor": mp["proveedor"],
                        "esta_activo": True
                    }
                )

            # 2️⃣ Agencias de Envío
            agencias = [
                {"nombre": "DHL Express", "contacto": "Juan Pérez", "telefono": "800-1234"},
                {"nombre": "Correo Bolivia", "contacto": "María López", "telefono": "800-9012"},
            ]
            for ag in agencias:
                Agencia.objects.get_or_create(
                    nombre=ag["nombre"],
                    empresa=empresa,
                    defaults={
                        "contacto": ag["contacto"],
                        "telefono": ag["telefono"],
                        "esta_activo": True
                    }
                )

            # 3️⃣ Datos por empresa
            usuarios = User.objects.filter(empresa=empresa)
            sucursales = Sucursal.objects.filter(empresa=empresa)
            metodos = Metodo_pago.objects.filter(empresa=empresa)
            agencias_empresa = Agencia.objects.filter(empresa=empresa)
            
            if not sucursales.exists():
                self.stdout.write(f"    ⚠️ No hay sucursales para {empresa.nombre}, saltando...")
                continue

            # 4️⃣ Obtener el último número de nota usado para esta empresa
            ultima_venta = Venta.objects.filter(empresa=empresa).order_by('-id').first()
            if ultima_venta and ultima_venta.numero_nota:
                try:
                    ultimo_numero = int(ultima_venta.numero_nota.split('-')[1])
                except (IndexError, ValueError):
                    ultimo_numero = 0
            else:
                ultimo_numero = 0

            # 5️⃣ Crear ventas por sucursal
            ventas_totales = 0
            
            for sucursal in sucursales:
                self.stdout.write(f"    🏪 Creando ventas para: {sucursal.nombre}")
                
                # ✅ PRODUCTOS CON STOCK EN ESTA SUCURSAL
                stocks_disponibles = StockSucursal.objects.filter(
                    empresa=empresa,
                    sucursal=sucursal,
                    stock__gt=0
                ).select_related('producto')
                
                if not stocks_disponibles.exists():
                    self.stdout.write(f"      ⚠️ Sin stock disponible en {sucursal.nombre}")
                    continue
                
                # Crear 2-4 ventas por sucursal
                for i in range(random.randint(2, 4)):
                    with transaction.atomic():
                        # ✅ GENERAR NÚMERO DE NOTA ÚNICO MANUALMENTE
                        numero_nota = f"NV-{ultimo_numero + 1:05d}"
                        ultimo_numero += 1
                        
                        # ✅ SELECCIONAR PRODUCTOS CON STOCK DISPONIBLE
                        productos_stock = random.sample(
                            list(stocks_disponibles), 
                            min(random.randint(1, 3), len(stocks_disponibles))
                        )
                        
                        # ✅ CREAR PAGO
                        metodo = random.choice(metodos)
                        pago = Pago.objects.create(
                            empresa=empresa,
                            metodo=metodo,
                            monto=0,  # Se calculará
                            estado="completado",
                            referencia=f"PAY-{empresa.id}-S{sucursal.id}-{i+1:03d}"
                        )
                        
                        # ✅ CREAR VENTA CON SUCURSAL Y NÚMERO MANUAL
                        usuario = random.choice(usuarios)
                        venta = Venta.objects.create(
                            empresa=empresa,
                            numero_nota=numero_nota,  # ✅ NÚMERO MANUAL ÚNICO
                            usuario=usuario,
                            sucursal=sucursal,
                            pago=pago,
                            total=0,  # Se calculará
                            estado=random.choice(["completado", "pendiente"]),
                            fecha=timezone.now()
                        )
                        
                        # ✅ DETALLES Y ACTUALIZAR STOCK
                        total_venta = 0
                        productos_vendidos = 0
                        
                        for stock_item in productos_stock:
                            producto = stock_item.producto
                            # Cantidad que se puede vender (no más del stock disponible)
                            max_cantidad = min(stock_item.stock, random.randint(1, 2))
                            if max_cantidad <= 0:
                                continue
                                
                            cantidad = max_cantidad
                            precio_unitario = producto.precio_venta
                            subtotal = cantidad * precio_unitario
                            total_venta += subtotal
                            productos_vendidos += 1
                            
                            # Crear detalle de venta
                            DetalleVenta.objects.create(
                                empresa=empresa,
                                venta=venta,
                                producto=producto,
                                cantidad=cantidad,
                                precio_unitario=precio_unitario,
                                subtotal=subtotal
                            )
                            
                            # ✅ ACTUALIZAR STOCK EN ESTA SUCURSAL
                            stock_item.stock -= cantidad
                            stock_item.save()
                            self.stdout.write(f"      📦 Stock actualizado: {producto.nombre} -{cantidad} (nuevo: {stock_item.stock})")
                        
                        # Si no se pudieron vender productos, eliminar la venta
                        if productos_vendidos == 0:
                            venta.delete()
                            pago.delete()
                            self.stdout.write(f"      ❌ Venta eliminada (sin stock disponible)")
                            ultimo_numero -= 1  # Revertir el contador
                            continue
                        
                        # Actualizar totales
                        venta.total = total_venta
                        venta.save()
                        pago.monto = total_venta
                        pago.save()
                        
                        ventas_totales += 1
                        self.stdout.write(f"      ✅ Venta {venta.numero_nota}: ${total_venta}")
                        
                        # ✅ ENVÍOS (30% probabilidad para ventas > $100)
                        if total_venta > 100 and random.random() < 0.3 and agencias_empresa.exists():
                            agencia = random.choice(agencias_empresa)
                            cliente = random.choice(usuarios)
                            Envio.objects.create(
                                empresa=empresa,
                                venta=venta,
                                cliente=cliente,
                                agencia=agencia,
                                estado=random.choice(["preparando", "en_transito"]),
                                esta_activo=True
                            )
                            self.stdout.write(f"      📦 Envío creado para {venta.numero_nota}")

            self.stdout.write(self.style.SUCCESS(f"✅ {ventas_totales} ventas creadas para {empresa.nombre}"))
        
        self.stdout.write(self.style.SUCCESS("\n🎯 Seed de ventas completado ✅"))