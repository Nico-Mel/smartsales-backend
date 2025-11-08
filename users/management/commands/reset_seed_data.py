from django.core.management.base import BaseCommand
from users.models import Role, Module, Permission, User
from sucursales.models import Sucursal

class Command(BaseCommand):
    help = 'Resetea los datos creados por el seeder inicial (Roles, Modules, Permissions, Sucursales y Usuarios no-admin)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando reseteo de datos del seeder...'))

        # 1. Borrar Permisos
        count, _ = Permission.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f' {count} Permisos eliminados.'))

        # 2. Borrar Módulos
        count, _ = Module.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f' {count} Módulos eliminados.'))

        # 3. Borrar Roles
        count, _ = Role.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f' {count} Roles eliminados.'))

        # 4. Borrar Sucursales
        count, _ = Sucursal.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f' {count} Sucursales eliminadas.'))

        # 5. Borrar Usuarios (EXCEPTO superusuarios)
        count, _ = User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS(f' {count} Usuarios (no-admin) eliminados.'))

        self.stdout.write(self.style.SUCCESS('\n Reseteo completado. El superusuario sigue existiendo.'))