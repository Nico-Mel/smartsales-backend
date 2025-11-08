# users/management/commands/reset_all_data.py
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection, transaction

class Command(BaseCommand):
    help = "⚠️ Elimina TODOS los datos de TODAS las tablas del proyecto (reset completo, sin eliminar las migraciones)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("🚨 INICIANDO RESETEO TOTAL DE LA BASE DE DATOS..."))
        self.stdout.write(self.style.WARNING("⚠️ Esto eliminará TODOS los datos de TODAS las tablas, incluyendo usuarios, productos, etc."))
        confirm = input("¿Seguro que deseas continuar? (escribe 'yes' para confirmar): ")

        if confirm.lower() != "yes":
            self.stdout.write(self.style.ERROR("❌ Operación cancelada."))
            return

        try:
            with transaction.atomic():
                cursor = connection.cursor()

                # Desactivar restricciones de FK temporalmente
                self.stdout.write("⏸️  Desactivando restricciones de clave foránea...")
                cursor.execute("SET session_replication_role = 'replica';")

                # Obtener todas las tablas del proyecto
                all_models = apps.get_models()
                deleted_tables = []

                for model in all_models:
                    table = model._meta.db_table
                    try:
                        cursor.execute(f"TRUNCATE TABLE \"{table}\" RESTART IDENTITY CASCADE;")
                        deleted_tables.append(table)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"⚠️ No se pudo truncar {table}: {e}"))

                # Reactivar las FK
                cursor.execute("SET session_replication_role = 'origin';")

                self.stdout.write(self.style.SUCCESS("✅ Restricciones restauradas."))
                self.stdout.write(self.style.SUCCESS(f"💥 Tablas limpiadas ({len(deleted_tables)}):"))
                for t in deleted_tables:
                    self.stdout.write(f"  - {t}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error durante el reseteo: {e}"))
            return

        self.stdout.write(self.style.SUCCESS("\n🎉 RESETEO TOTAL COMPLETADO EXITOSAMENTE ✅"))
        self.stdout.write(self.style.WARNING("👉 Ahora ejecuta los seeders:"))
        self.stdout.write(self.style.HTTP_INFO("python manage.py seed_users_data"))
        self.stdout.write(self.style.HTTP_INFO("python manage.py seed_sample_data"))
