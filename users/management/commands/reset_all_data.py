# users/management/commands/reset_all_data.py
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection

class Command(BaseCommand):
    help = "⚠️ Elimina TODOS los datos de TODAS las tablas del proyecto"

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Ejecuta el reset sin pedir confirmación.',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("🚨 RESETEO TOTAL DE LA BASE DE DATOS..."))

        if not options['no_input']:
            confirm = input("¿Seguro? (escribe 'yes'): ")
            if confirm.lower() != "yes":
                self.stdout.write(self.style.ERROR("❌ Cancelado."))
                return
        
        try:
            cursor = connection.cursor()
            
            # SOLO TRUNCATE SIN TRANSACCIÓN COMPLEJA
            all_models = apps.get_models()
            for model in all_models:
                table = model._meta.db_table
                try:
                    cursor.execute(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE;')
                    self.stdout.write(f"✅ {table}")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"⚠️ {table}: {e}"))

            self.stdout.write(self.style.SUCCESS("🎉 RESET COMPLETADO"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))