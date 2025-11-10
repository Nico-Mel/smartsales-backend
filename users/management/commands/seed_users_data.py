# users/management/commands/seed_users_data.py
from django.core.management.base import BaseCommand
from users.models import Role, Module, Permission, User
from tenants.models import Empresa, Plan
from sucursales.models import Sucursal, Direccion, Departamento


class Command(BaseCommand):
    help = "🌱 Configura datos base multiempresa de SmartSales365 (SaaS)"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING("=== 🌱 Configurando datos base multiempresa SmartSales365 ==="))

        # ====== PLAN ======
        plan, _ = Plan.objects.get_or_create(
            nombre="PREMIUM",
            defaults={
                "descripcion": "Plan con todas las funcionalidades",
                "max_usuarios": 50,
                "max_productos": 500,
                "precio_mensual": 99.99,
                "permite_reportes_ia": True,
                "permite_exportar_excel": True,
                "permite_notificaciones_push": True,
                "soporte_prioritario": True,
                "esta_activo": True,
            },
        )

        # ====== EMPRESAS ======
        empresas = [
            {"nombre": "SmartSales S.R.L.", "nit": "987654321"},
            {"nombre": "TechWorld S.A.", "nit": "123456789"},
        ]
        empresas_creadas = []
        for e in empresas:
            emp, _ = Empresa.objects.get_or_create(
                nombre=e["nombre"],
                defaults={"nit": e["nit"], "plan": plan, "esta_activo": True},
            )
            empresas_creadas.append(emp)
            self.stdout.write(self.style.SUCCESS(f"🏢 Empresa asegurada: {emp.nombre}"))

        # ====== DEPARTAMENTOS PARA TODAS LAS EMPRESAS EXISTENTES ======
        departamentos_data = ["Santa Cruz", "La Paz", "Cochabamba"]
        empresas_existentes = Empresa.objects.all()

        # Diccionario para guardar referencias de departamentos por empresa
        departamentos_por_empresa = {}

        for empresa in empresas_existentes:
            self.stdout.write(f"📝 Poblando departamentos para: {empresa.nombre}")
            departamentos_empresa = {}
            for depto_nombre in departamentos_data:
                dep, created = Departamento.objects.get_or_create(
                    nombre=depto_nombre,
                    empresa=empresa,
                    defaults={}
                )
                departamentos_empresa[depto_nombre] = dep
                status = self.style.SUCCESS("✅ CREADO") if created else self.style.NOTICE("⚠️ YA EXISTÍA")
                self.stdout.write(f"  {status} Departamento: {depto_nombre}")
            
            departamentos_por_empresa[empresa.id] = departamentos_empresa

        # ====== ROLES ======
        roles_data = [
            {"name": "SUPER_ADMIN", "description": "Administrador global del sistema"},
            {"name": "ADMIN", "description": "Administrador de empresa"},
            {"name": "SALES_AGENT", "description": "Agente de ventas"},
            {"name": "CUSTOMER", "description": "Cliente final"},
        ]
        roles = {}
        for r in roles_data:
            role, _ = Role.objects.get_or_create(name=r["name"], defaults={"description": r["description"]})
            roles[r["name"]] = role
            self.stdout.write(self.style.SUCCESS(f"✅ Rol asegurado: {role.name}"))

        # ====== SUPER ADMIN GLOBAL ======
        superadmin, created = User.objects.get_or_create(
            email="owner@smartsales365.com",
            defaults={
                "nombre": "SaaS Owner",
                "apellido": "Global",
                "telefono": "00000000",
                "is_superuser": True,
                "is_staff": True,
                "empresa": None,
                "role": roles["SUPER_ADMIN"],
            },
        )
        if created:
            superadmin.set_password("owner123")
            superadmin.save()
        self.stdout.write(self.style.SUCCESS("🌍 SUPER ADMIN global listo (owner@smartsales365.com / owner123)"))

        # ====== ADMIN POR EMPRESA ======
        admins = [
            {"email": "admin1@smartsales.com", "empresa": empresas_creadas[0]},
            {"email": "admin2@techworld.com", "empresa": empresas_creadas[1]},
        ]
        for adm in admins:
            user, created = User.objects.get_or_create(
                email=adm["email"],
                defaults={
                    "nombre": "Admin",
                    "apellido": adm["empresa"].nombre,
                    "telefono": "70000000",
                    "empresa": adm["empresa"],
                    "role": roles["ADMIN"],
                    "is_staff": True,
                },
            )
            if created:
                user.set_password("admin123")
                user.save()
            self.stdout.write(self.style.SUCCESS(f"👑 Admin listo: {adm['email']} / admin123"))

        # ====== MÓDULOS ======
        modules_data = [
            {"name": "User", "description": "Gestión de usuarios"},
            {"name": "Role", "description": "Gestión de roles"},
            {"name": "Module", "description": "Gestión de módulos"},
            {"name": "Permission", "description": "Gestión de permisos"},
            {"name": "Marca", "description": "Gestión de marcas"},
            {"name": "Categoria", "description": "Gestión de categorías"},
            {"name": "SubCategoria", "description": "Gestión de subcategorías"},
            {"name": "Producto", "description": "Gestión de productos"},
            {"name": "DetalleProducto", "description": "Gestión de detalles"},
            {"name": "ImagenProducto", "description": "Gestión de imágenes"},
            {"name": "Campania", "description": "Gestión de campañas"},
            {"name": "Descuento", "description": "Gestión de descuentos"},
            {"name": "Sucursal", "description": "Gestión de sucursales"},
            {"name": "StockSucursal", "description": "Gestión de stock"},
            {"name": "Bitacora", "description": "Registro de acciones"},
            {"name": "Empresa", "description": "Gestión de empresas"},
            {"name": "Plan", "description": "Gestión de planes"},
            {"name": "Metodo_pago", "description": "Gestión de métodos de pago"},
            {"name": "Pago", "description": "Gestión de pagos"},
            {"name": "Venta", "description": "Gestión de ventas"},
            {"name": "DetalleVenta", "description": "Gestión de detalles de venta"},
            {"name": "Agencia", "description": "Gestión de agencias de envío"},
            {"name": "Envio", "description": "Gestión de envíos"},
            {"name": "Direccion", "description": "Gestión de direcciones"},
            {"name": "Departamento", "description": "Gestión de departamentos"},
            {"name": "Notificacion", "description": "Gestión de notificaciones"},
            {"name": "Reporte", "description": "Gestión de reportes"},
            {"name": "IAReport", "description": "Generación de reportes con IA"},

        ]
        modules = {}
        for m in modules_data:
            mod, _ = Module.objects.get_or_create(name=m["name"], defaults={"description": m["description"]})
            modules[m["name"]] = mod

        # ====== PERMISOS ======
        for role_name, full_access in {"SUPER_ADMIN": True, "ADMIN": True}.items():
            for mod in modules.values():
                Permission.objects.get_or_create(
                    role=roles[role_name],
                    module=mod,
                    defaults={
                        "can_view": 1,
                        "can_create": int(full_access),
                        "can_update": int(full_access),
                        "can_delete": int(full_access),
                    },
                )

        # ====== SUCURSALES POR EMPRESA ======
        for emp in empresas_creadas:
            depto_santa_cruz = departamentos_por_empresa[emp.id]["Santa Cruz"]
            depto_la_paz = departamentos_por_empresa[emp.id]["La Paz"]
            
            # Sucursal Central (Santa Cruz)
            direccion_central, _ = Direccion.objects.get_or_create(
                empresa=emp,
                pais="Bolivia",
                ciudad="Santa Cruz de la Sierra", 
                zona="Centro",
                calle=f"Av. {emp.nombre.split()[0]} Central",
                numero="101",
                departamento=depto_santa_cruz,
            )
            Sucursal.objects.get_or_create(
                empresa=emp,
                nombre=f"Sucursal Central - {emp.nombre.split()[0]}",
                direccion=direccion_central,
                defaults={"esta_activo": True},
            )
            
            # Sucursal La Paz (La Paz)
            direccion_lp, _ = Direccion.objects.get_or_create(
                empresa=emp,
                pais="Bolivia",
                ciudad="La Paz", 
                zona="Zona Norte",
                calle=f"Av. {emp.nombre.split()[0]} La Paz",
                numero="202",
                departamento=depto_la_paz,
            )
            Sucursal.objects.get_or_create(
                empresa=emp,
                nombre=f"Sucursal La Paz - {emp.nombre.split()[0]}",
                direccion=direccion_lp,
                defaults={"esta_activo": True},
            )
            
            # Sucursal Norte (Santa Cruz - otra zona)
            direccion_norte, _ = Direccion.objects.get_or_create(
                empresa=emp,
                pais="Bolivia",
                ciudad="Santa Cruz de la Sierra", 
                zona="Equipetrol",
                calle=f"Av. {emp.nombre.split()[0]} Norte",
                numero="303",
                departamento=depto_santa_cruz,
            )
            Sucursal.objects.get_or_create(
                empresa=emp,
                nombre=f"Sucursal Norte - {emp.nombre.split()[0]}",
                direccion=direccion_norte,
                defaults={"esta_activo": True},
            )
            
            self.stdout.write(self.style.SUCCESS(f"🏪 3 Sucursales creadas para {emp.nombre}"))

        self.stdout.write(self.style.SUCCESS("\n🎉 Configuración de múltiples empresas completada ✅"))
        self.stdout.write(self.style.SUCCESS("📊 Tablas pobladas: Departamento, Plan, Empresa, Role, User, Module, Permission, Direccion, Sucursal"))