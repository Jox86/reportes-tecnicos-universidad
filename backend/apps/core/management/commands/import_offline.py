# backend/apps/core/management/commands/import_offline.py
"""
Importa datos exportados con `sync_offline` evitando duplicados.

Estrategia:
- Catálogos (TipoArea, TipoTarea, Area, Ubicacion): si existe la PK o el nombre, saltar.
- Reportes y relacionados: crear siempre con nueva PK.
- Foreign keys: convertir IDs a instancias del modelo.
"""
import json
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction


# Mapeo de campos FK: {"modelo": ["campo1", "campo2"]}
CAMPOS_FK = {
    "core.area": ["tipo_area"],
    "core.ubicacion": ["area"],
    "core.reporte": ["tipo_tarea", "area", "creado_por", "tecnico_asignado"],
    "core.equiporeporte": ["reporte"],
    "core.historialestado": ["reporte", "usuario"],
}


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
        mapa_reportes = {}  # mapa de PKs viejas → nuevas de reportes

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

            # ¿Ya existe? (para catálogos)
            existente = None
            if modelo_str in self.CATALOGOS:
                # Buscar por PK O por campo único (nombre)
                existente = Modelo.objects.filter(pk=pk).first()
                if not existente and "nombre" in campos:
                    existente = Modelo.objects.filter(nombre=campos["nombre"]).first()

            if existente and modelo_str in self.CATALOGOS:
                saltados += 1
                continue

            if modelo_str == "core.reporte":
                existente_reporte = Modelo.objects.filter(pk=pk).first()
                if existente_reporte:
                    saltados += 1
                    continue

            try:
                if dry_run:
                    self.stdout.write(f"  [DRY] {modelo_str} pk={pk}")
                    creados += 1
                    continue

                with transaction.atomic():
                    # Convertir campos FK de IDs a instancias
                    for campo_fk in CAMPOS_FK.get(modelo_str, []):
                        valor_id = campos.get(campo_fk)
                        if valor_id is None:
                            continue

                        # Si el valor ya es un dict (natural_key), ignorar
                        if isinstance(valor_id, (list, dict)):
                            continue

                        # Determinar el modelo destino
                        campo_meta = Modelo._meta.get_field(campo_fk)
                        ModeloDestino = campo_meta.related_model

                        # Para reportes, si es FK a Reporte, buscar en el mapa
                        if modelo_str in ("core.equiporeporte", "core.historialestado") and campo_fk == "reporte":
                            nueva_pk = mapa_reportes.get(valor_id)
                            if nueva_pk:
                                campos[campo_fk] = ModeloDestino.objects.get(pk=nueva_pk)
                            else:
                                # Buscar el reporte original
                                campos[campo_fk] = ModeloDestino.objects.get(pk=valor_id)
                        else:
                            try:
                                campos[campo_fk] = ModeloDestino.objects.get(pk=valor_id)
                            except ModeloDestino.DoesNotExist:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"  ⚠ {modelo_str}: FK {campo_fk}={valor_id} no existe, ignorando"
                                    )
                                )
                                campos[campo_fk] = None

                    if modelo_str in self.CON_NUEVA_PK:
                        # Crear sin la PK original
                        obj = Modelo(**campos)
                        obj.save()
                        if modelo_str == "core.reporte":
                            mapa_reportes[pk] = obj.pk
                    else:
                        obj = Modelo(**campos)
                        obj.pk = pk
                        obj.save(force_insert=True)

                creados += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ {modelo_str} pk={pk}"))
            except Exception as e:
                errores += 1
                self.stdout.write(self.style.ERROR(f"  ✗ {modelo_str} pk={pk}: {e}"))

        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS(f"  ✓ Creados: {creados}"))
        self.stdout.write(f"  · Saltados: {saltados}")
        self.stdout.write(self.style.ERROR(f"  ✗ Errores: {errores}"))
        self.stdout.write("=" * 60)