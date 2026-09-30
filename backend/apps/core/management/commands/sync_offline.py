# backend/apps/core/management/commands/sync_offline.py
from django.core.management.base import BaseCommand
from django.core.management import call_command
from io import StringIO


class Command(BaseCommand):
    help = "Exporta datos de las apps de negocio a JSON para sincronización offline."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="offline_sync.json",
            help="Ruta del archivo de salida (default: offline_sync.json)",
        )

    def handle(self, *args, **options):
        output_file = options["output"]
        apps_to_sync = ["core", "stats", "accounts"]

        self.stdout.write(
            self.style.NOTICE(f"Exportando datos de: {', '.join(apps_to_sync)}")
        )

        buffer = StringIO()
        call_command(
            "dumpdata",
            *apps_to_sync,
            indent=2,
            stdout=buffer,
            natural_foreign=True,
            natural_primary=True,
        )

        contenido = buffer.getvalue()

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(contenido)

        self.stdout.write(self.style.SUCCESS(f"✓ Archivo creado: {output_file} (UTF-8)"))