# users/management/commands/seed_users_data.py
from django.core.management.base import BaseCommand
from users.models import Role, Module, Permission, User, UserStatus

# ✅ Importa el modelo Sucursal
from sucursales.models import Sucursal


class Command(BaseCommand):
    help = 'Seeder inicial: Roles, Modules, Permissions, Usuario Admin y Sucursal base'

    def handle(self, *args, **kwargs):

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
            {'name': 'Producto', 'description': 'Gestión de productos'},
            {'name': 'ProductoCategoria', 'description': 'Relación producto-categoría'},
            {'name': 'DetalleProducto', 'description': 'Gestión de detalles del producto'},
            {'name': 'ImagenProducto', 'description': 'Gestión de imágenes del producto'},
            {'name': 'Campania', 'description': 'Gestión de campañas de marketing'},
            {'name': 'Descuento', 'description': 'Gestión de descuentos y promociones'},

            # ---- Ventas (futuro) ----
            {'name': 'Sales', 'description': 'Gestión de ventas y reportes'},
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
            {'role': 'ADMIN', 'module': 'Producto', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},
            {'role': 'ADMIN', 'module': 'ProductoCategoria', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},
            {'role': 'ADMIN', 'module': 'DetalleProducto', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},
            {'role': 'ADMIN', 'module': 'ImagenProducto', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},
            {'role': 'ADMIN', 'module': 'Campania', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},
            {'role': 'ADMIN', 'module': 'Descuento', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},
            {'role': 'ADMIN', 'module': 'Sales', 'view': 1, 'create': 1, 'update': 1, 'delete': 1},

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
        msg = "creada" if created else "ya existía"
        self.stdout.write(self.style.SUCCESS(f"🏢 Sucursal {msg}: {sucursal.nombre}"))


        self.stdout.write(self.style.SUCCESS("\n🎉 Seeder completo: Roles, módulos, permisos y sucursal base creados exitosamente ✅"))
