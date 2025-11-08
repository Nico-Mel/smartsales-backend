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
            {"name": "Stock", "description": "Gestión de stock"},
            {"name": "Bitacora", "description": "Registro de acciones"},
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
        departamento, _ = Departamento.objects.get_or_create(nombre="La Paz")
        for emp in empresas_creadas:
            direccion, _ = Direccion.objects.get_or_create(
                empresa=emp,
                pais="Bolivia",
                ciudad="La Paz",
                zona="Centro",
                calle=f"Av. {emp.nombre.split()[0]} Central",
                numero="101",
                departamento=departamento,
            )
            Sucursal.objects.get_or_create(
                empresa=emp,
                nombre=f"Sucursal Central - {emp.nombre.split()[0]}",
                direccion=direccion,
                defaults={"esta_activo": True},
            )

        self.stdout.write(self.style.SUCCESS("\n🎉 Configuración de múltiples empresas completada ✅"))
