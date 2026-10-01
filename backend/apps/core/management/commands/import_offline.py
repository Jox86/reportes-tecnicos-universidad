# backend/apps/core/management/commands/import_offline.py
"""
Importa datos exportados con `sync_offline` evitando duplicados.

Estrategia:
- Catálogos (TipoArea, TipoTarea, Area, Ubicacion): si existe la PK, saltar.
- Reportes y relacionados: crear siempre con nueva PK (evita conflictos).
"""
import json
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction


class Command(BaseCommand):
    help = "Importa datos offline evitando duplicados."

    # Catálogos: si existe la PK, saltar. No actualizar.
    CATALOGOS = [
        "core.tipoarea",
        "core.tipotarea",
        "core.area",
        "core.ubicacion",
    ]

    # Reportes: crear siempre con nueva PK (evita conflictos)
    CON_NUEVA_PK = [
        "core.reporte",
        "core.equiporeporte",
        "core.historialestado",
    ]

    def add_arguments(self, parser):
        parser.add_argument("input_file", type=str, help="Archivo JSON a importar")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Solo simular, no guardar cambios",
        )

    def handle(self, *args, **options):
        input_file = options["input_file"]
        dry_run = options["dry_run"]

        with open(input_file, "r", encoding="utf-8") as f:
            datos = json.load(f)

        self.stdout.write(
            self.style.NOTICE(f"Importando {len(datos)} registros desde {input_file}")
        )
        if dry_run:
            self.stdout.write(self.style.WARNING("⚠ MODO DRY-RUN: no se guardarán cambios"))

        creados = 0
        saltados = 0
        errores = 0

        # Mapeo de reportes antiguos → nuevos para actualizar FKs
        mapa_reportes = {}

        for item in datos:
            modelo_str = item["model"]
            pk = item["pk"]
            campos = item["fields"]

            try:
                app_label, model_name = modelo_str.split(".")
                Modelo = apps.get_model(app_label, model_name)
            except LookupError:
                self.stdout.write(self.style.WARNING(f"  ✗ Modelo no encontrado: {modelo_str}"))
                errores += 1
                continue

            # ¿Ya existe?
            existente = Modelo.objects.filter(pk=pk).first()

            # Catálogos: saltar si existe
            if existente and modelo_str in self.CATALOGOS:
                saltados += 1
                continue

            # Reportes: si el reporte ya existe por código, saltar
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
                        # Reasignar FKs de reporte a los nuevos IDs
                        if modelo_str in ("core.equiporeporte", "core.historialestado"):
                            reporte_viejo = campos.get("reporte")
                            if reporte_viejo in mapa_reportes:
                                campos["reporte"] = mapa_reportes[reporte_viejo]

                        # Crear sin PK original (Django asigna una nueva)
                        obj = Modelo(**campos)
                        obj.save()

                        # Guardar el mapeo si es un reporte
                        if modelo_str == "core.reporte":
                            mapa_reportes[pk] = obj.pk
                    else:
                        # Crear con PK original
                        obj = Modelo(**campos)
                        obj.pk = pk
                        obj.save(force_insert=True)

                creados += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ {modelo_str} pk={pk}"))

            except Exception as e:
                errores += 1
                self.stdout.write(self.style.ERROR(f"  ✗ {modelo_str} pk={pk}: {e}"))

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"  ✓ Creados: {creados}"))
        self.stdout.write(f"  · Saltados (ya existían): {saltados}")
        if errores:
            self.stdout.write(self.style.ERROR(f"  ✗ Errores: {errores}"))
        self.stdout.write("=" * 60)