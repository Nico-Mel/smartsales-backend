# users/management/commands/seed_users_data.py
from django.core.management.base import BaseCommand
from users.models import Role, Module, Permission, User
from tenants.models import Empresa, Plan
from sucursales.models import Sucursal, Direccion, Departamento


class Command(BaseCommand):
    help = "Actualiza los roles, empresa y campos del usuario admin existente sin duplicar registros"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING("=== ACTUALIZANDO DATOS SmartSales365 EXISTENTES ==="))

        # ====== 1️⃣ ROLES ======
        roles_data = [
            {'name': 'ADMIN', 'description': 'Administrador del sistema'},
            {'name': 'SALES_AGENT', 'description': 'Agente de Ventas'},
            {'name': 'CUSTOMER', 'description': 'Cliente final'},
        ]

        roles = {}
        for r in roles_data:
            role, created = Role.objects.get_or_create(
                name=r['name'],
                defaults={'description': r['description']}
            )
            roles[r['name']] = role
            msg = "creado" if created else "ya existía"
            self.stdout.write(self.style.SUCCESS(f"✅ Rol {msg}: {role.name}"))

        # ====== 2️⃣ USUARIO ADMINISTRADOR ======
        admin_email = 'admin@smartsales.com'
        admin_password = 'admin123'

        if not User.objects.filter(email=admin_email).exists():
            admin_user = User.objects.create_superuser(
                email=admin_email,
                password=admin_password,
                nombre='Administrador',
                apellido='Principal',
                telefono='70000000',
                role=roles['ADMIN'],
                status=UserStatus.ACTIVE
            )
            self.stdout.write(self.style.SUCCESS(f"👑 Usuario administrador creado: {admin_user.email}"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ Usuario administrador ya existe: {admin_email}"))

        # ====== 3️⃣ MÓDULOS ======
        modules_data = [
            # ---- Usuarios y Roles ----
            {'name': 'User', 'description': 'Gestión de usuarios'},
            {'name': 'Role', 'description': 'Gestión de roles'},
            {'name': 'Module', 'description': 'Gestión de módulos'},
            {'name': 'Permission', 'description': 'Gestión de permisos'},

            # ---- Productos ----
            {'name': 'Marca', 'description': 'Gestión de marcas'},
            {'name': 'Categoria', 'description': 'Gestión de categorías de productos'},
            {'name': 'SubCategoria', 'description': 'Gestión de subcategorías'}, 
            {'name': 'Producto', 'description': 'Gestión de productos'},
            {'name': 'ProductoCategoria', 'description': 'Relación producto-categoría'},
            {'name': 'DetalleProducto', 'description': 'Gestión de detalles del producto'},
            {'name': 'ImagenProducto', 'description': 'Gestión de imágenes del producto'},
            {'name': 'Campania', 'description': 'Gestión de campañas de marketing'},
            {'name': 'Descuento', 'description': 'Gestión de descuentos y promociones'},

            # ---- Inventario y Sucursales ----
            {'name': 'Sucursal', 'description': 'Gestión de sucursales'}, 
            {'name': 'Stock', 'description': 'Gestión de stock en sucursales'}, 

            # ---- Otros ----
            {'name': 'Sales', 'description': 'Gestión de ventas y reportes'},
            {'name': 'Bitacora', 'description': 'Registro de acciones del sistema'},
        ]

        modules = {}
        for m in modules_data:
            module, created = Module.objects.get_or_create(
                name=m['name'],
                defaults={'description': m['description'], 'is_active': True}
            )
            modules[m['name']] = module
            msg = "creado" if created else "ya existía"
            self.stdout.write(self.style.SUCCESS(f"📦 Módulo {msg}: {module.name}"))

        # ====== 4️⃣ PERMISOS ======
        perms_data = [

            # ---- ADMIN: acceso total a todo ----
            {'role': 'ADMIN', 'module': 'User', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},
            {'role': 'ADMIN', 'module': 'Role', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},
            {'role': 'ADMIN', 'module': 'Module', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},
            {'role': 'ADMIN', 'module': 'Permission', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},

            {'role': 'ADMIN', 'module': 'Marca', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},
            {'role': 'ADMIN', 'module': 'Categoria', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},
            {'role': 'ADMIN', 'module': 'SubCategoria', 'view': 1, 'create': 1, 'update': 1, 'delete': 1}, 
            {'role': 'ADMIN', 'module': 'Producto', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},
            {'role': 'ADMIN', 'module': 'ProductoCategoria', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},
            {'role': 'ADMIN', 'module': 'DetalleProducto', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},
            {'role': 'ADMIN', 'module': 'ImagenProducto', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},
            {'role': 'ADMIN', 'module': 'Campania', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},
            {'role': 'ADMIN', 'module': 'Descuento', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},
            
            {'role': 'ADMIN', 'module': 'Sucursal', 'view': 1, 'create': 1, 'update': 1, 'delete': 1}, 
            {'role': 'ADMIN', 'module': 'Stock', 'view': 1, 'create': 1, 'update': 1, 'delete': 1}, 

            {'role': 'ADMIN', 'module': 'Sales', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},
            {'role': 'ADMIN', 'module': 'Bitacora', 'view': 1, 'create': 1, 'update': 1, 'delete': 1}, 
            # ---- SALES_AGENT: permisos limitados ----
            {'role': 'SALES_AGENT', 'module': 'Producto', 'view': 1, 'create': 0, 'update': 0, 'delete': 0},
            {'role': 'SALES_AGENT', 'module': 'Campania', 'view': 1, 'create': 0, 'update': 0, 'delete': 0},
            {'role': 'SALES_AGENT', 'module': 'Descuento', 'view': 1, 'create': 0, 'update': 0, 'delete': 0},

            # ---- CUSTOMER: solo puede ver productos ----
            {'role': 'CUSTOMER', 'module': 'Producto', 'view': 1, 'create': 0, 'update': 0, 'delete': 0},
            {'role': 'CUSTOMER', 'module': 'Categoria', 'view': 1, 'create': 0, 'update': 0, 'delete': 0},
        ]

        for p in perms_data:
            perm, created = Permission.objects.get_or_create(
                role=roles[p['role']],
                module=modules[p['module']],
                defaults={
                    'can_view': p['view'],
                    'can_create': p['create'],
                    'can_update': p['update'],
                    'can_delete': p['delete'],
                }
            )
            msg = "creado" if created else "ya existía"
            self.stdout.write(self.style.SUCCESS(f"🔐 Permiso {msg}: {p['role']} → {p['module']}"))


        # ====== 5️⃣ SUCURSAL BASE ======
        sucursal, created = Sucursal.objects.get_or_create(
            nombre="Sucursal Central",
            defaults={'esta_activo': True}
        )
        empresa, _ = Empresa.objects.get_or_create(
            nombre="SmartSales S.R.L.",
            defaults={"nit": "987654321", "plan": plan, "esta_activo": True},
        )
        self.stdout.write(self.style.SUCCESS(f"🏢 Empresa asegurada: {empresa.nombre}"))

        # ================================
        # 2️⃣ ROLES EXISTENTES → Actualizar empresa
        # ================================
        roles_actualizados = 0
        for role in Role.objects.all():
            if not role.empresa:
                role.empresa = empresa
                role.save()
                roles_actualizados += 1
        self.stdout.write(self.style.SUCCESS(f"✅ Roles actualizados con empresa: {roles_actualizados}"))

        # ================================
        # 3️⃣ USUARIO ADMIN EXISTENTE
        # ================================
        admin_email = "admin@smartsales.com"
        try:
            admin_user = User.objects.get(email=admin_email)
            admin_user.empresa = empresa
            admin_user.role = Role.objects.filter(name="ADMIN").first()
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"👑 Usuario admin actualizado: {admin_user.email}"))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ No se encontró usuario admin@smartsales.com"))

        # ================================
        # 4️⃣ SUCURSAL BASE (si no existe)
        # ================================
        departamento, _ = Departamento.objects.get_or_create(nombre="La Paz")
        direccion, _ = Direccion.objects.get_or_create(
            empresa=empresa,
            pais="Bolivia",
            ciudad="La Paz",
            zona="Centro",
            calle="Av. Mariscal Santa Cruz",
            numero="101",
            departamento=departamento,
        )
        Sucursal.objects.get_or_create(
            empresa=empresa,
            nombre="Sucursal Central",
            direccion=direccion,
            defaults={"esta_activo": True},
        )
        self.stdout.write(self.style.SUCCESS("🏬 Sucursal base asegurada"))

        self.stdout.write(self.style.SUCCESS("\n🎉 ACTUALIZACIÓN COMPLETA SIN DUPLICADOS ✅"))
