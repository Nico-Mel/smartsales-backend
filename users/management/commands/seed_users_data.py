# apps/users/management/commands/seed_users_data.py
from django.core.management.base import BaseCommand
from users.models import Role, Module, Permission, User, UserStatus

class Command(BaseCommand):
    help = 'Seeder inicial: Roles, Modules, Permissions y Usuario Admin'

    def handle(self, *args, **kwargs):

        # ----- ROLES -----
        roles_data = [
            {'name': 'ADMIN', 'description': 'Administrador'},
            {'name': 'SALES_AGENT', 'description': 'Agente de Ventas'},
            {'name': 'CUSTOMER', 'description': 'Cliente'},
        ]

        roles = {}
        for r in roles_data:
            role, created = Role.objects.get_or_create(
                name=r['name'],
                defaults={'description': r['description']}
            )
            roles[r['name']] = role
            if created:
                self.stdout.write(self.style.SUCCESS(f"Rol creado: {role.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Rol ya existe: {role.name}"))

        # ----- USUARIO ADMINISTRADOR -----
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
            self.stdout.write(self.style.SUCCESS(f"Usuario administrador creado: {admin_user.email}"))
        else:
            self.stdout.write(self.style.WARNING(f"Usuario administrador ya existe: {admin_email}"))

        # ----- MODULES -----
        modules_data = [
            {'name': 'User', 'description': 'Gestión de usuarios'},
            {'name': 'Role', 'description': 'Gestión de roles'},
            {'name': 'Module', 'description': 'Gestión de módulos'},
            {'name': 'Permission', 'description': 'Gestión de permisos'},
            {'name': 'Product', 'description': 'Gestión de productos'},
            {'name': 'Sales', 'description': 'Gestión de ventas'},
        ]

        modules = {}
        for m in modules_data:
            module, created = Module.objects.get_or_create(
                name=m['name'],
                defaults={'description': m['description'], 'is_active': True}
            )
            modules[m['name']] = module
            if created:
                self.stdout.write(self.style.SUCCESS(f"Módulo creado: {module.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Módulo ya existe: {module.name}"))

        # ----- PERMISSIONS -----
        perms_data = [
            # ADMIN: todos permisos
            {'role': 'ADMIN', 'module': 'User', 'can_view': True, 'can_create': True, 'can_update': True, 'can_delete': True},
            {'role': 'ADMIN', 'module': 'Module', 'can_view': True, 'can_create': True, 'can_update': True, 'can_delete': True},

            # SALES_AGENT: solo algunos permisos
            {'role': 'SALES_AGENT', 'module': 'User', 'can_view': True, 'can_create': False, 'can_update': False, 'can_delete': False},
        ]

        for p in perms_data:
            perm, created = Permission.objects.get_or_create(
                role=roles[p['role']],
                module=modules[p['module']],
                defaults={
                    'can_view': p['can_view'],
                    'can_create': p['can_create'],
                    'can_update': p['can_update'],
                    'can_delete': p['can_delete'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Permiso creado: {p['role']} -> {p['module']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Permiso ya existe: {p['role']} -> {p['module']}"))

        self.stdout.write(self.style.SUCCESS("Seeder inicial completado"))
