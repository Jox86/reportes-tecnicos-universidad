# backend/apps/core/management/commands/import_offline.py
import json
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction


class Command(BaseCommand):
    help = "Importa datos offline evitando duplicados."

    CATALOGOS = ["core.tipoarea", "core.tipotarea", "core.area", "core.ubicacion"]
    CON_NUEVA_PK = ["core.reporte", "core.equiporeporte", "core.historialestado"]

    def add_arguments(self, parser):
        parser.add_argument("input_file", type=str)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        input_file = options["input_file"]
        dry_run = options["dry_run"]

        with open(input_file, "r", encoding="utf-8") as f:
            datos = json.load(f)

        self.stdout.write(self.style.NOTICE(f"Importando {len(datos)} registros"))
        if dry_run:
            self.stdout.write(self.style.WARNING("Modo DRY-RUN"))

        creados = saltados = errores = 0
        mapa_reportes = {}

        for item in datos:
            modelo_str = item["model"]
            pk = item["pk"]
            campos = item["fields"]

            try:
                app_label, model_name = modelo_str.split(".")
                Modelo = apps.get_model(app_label, model_name)
            except LookupError:
                errores += 1
                continue

            existente = Modelo.objects.filter(pk=pk).first()

            if existente and modelo_str in self.CATALOGOS:
                saltados += 1
                continue

            if modelo_str == "core.reporte" and existente:
                saltados += 1
                continue

            try:
                if dry_run:
                    self.stdout.write(f"  [DRY] {modelo_str} pk={pk}")
                    creados += 1
                    continue

                with transaction.atomic():
                    if modelo_str in self.CON_NUEVA_PK:
                        if modelo_str in ("core.equiporeporte", "core.historialestado"):
                            rv = campos.get("reporte")
                            if rv in mapa_reportes:
                                campos["reporte"] = mapa_reportes[rv]
                        obj = Modelo(**campos)
                        obj.save()
                        if modelo_str == "core.reporte":
                            mapa_reportes[pk] = obj.pk
                    else:
                        obj = Modelo(**campos)
                        obj.pk = pk
                        obj.save(force_insert=True)
                creados += 1
                self.stdout.write(self.style.SUCCESS(f"  OK {modelo_str} pk={pk}"))
            except Exception as e:
                errores += 1
                self.stdout.write(self.style.ERROR(f"  ERROR {modelo_str} pk={pk}: {e}"))

        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS(f"  Creados: {creados}"))
        self.stdout.write(f"  Saltados: {saltados}")
        self.stdout.write(f"  Errores: {errores}")
        self.stdout.write("=" * 60)