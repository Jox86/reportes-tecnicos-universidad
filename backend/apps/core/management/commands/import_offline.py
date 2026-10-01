# backend/apps/core/management/commands/import_offline.py
"""
Importa datos exportados con `sync_offline` evitando duplicados.

Maneja:
- Catálogos: si existe la PK o el nombre, saltar.
- Reportes: crear siempre con nueva PK.
- Foreign keys: convertir IDs numéricos a instancias.
- Natural keys (listas como ["jfox6"]): resolver a instancias.
"""
import json
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction


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

    def resolver_fk(self, Modelo, campo_fk, valor, mapa_reportes=None):
        """
        Convierte un valor de FK a una instancia del modelo.
        Soporta:
        - ID numérico: 5
        - Natural key: ["jfox6"]
        """
        campo_meta = Modelo._meta.get_field(campo_fk)
        ModeloDestino = campo_meta.related_model

        # ¿Es una natural key? (lista o tupla)
        if isinstance(valor, (list, tuple)):
            try:
                return ModeloDestino._default_manager.get_by_natural_key(*valor)
            except ModeloDestino.DoesNotExist:
                return None

        # ¿Es un ID numérico?
        if isinstance(valor, int):
            # Para reportes, buscar en el mapa primero
            if ModeloDestino.__name__ == "Reporte" and mapa_reportes:
                nueva_pk = mapa_reportes.get(valor)
                if nueva_pk:
                    try:
                        return ModeloDestino.objects.get(pk=nueva_pk)
                    except ModeloDestino.DoesNotExist:
                        pass
            try:
                return ModeloDestino.objects.get(pk=valor)
            except ModeloDestino.DoesNotExist:
                return None

        return None

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
                self.stdout.write(self.style.WARNING(f"  ✗ Modelo no encontrado: {modelo_str}"))
                errores += 1
                continue

            # ¿Ya existe? (para catálogos, buscar por PK o por nombre)
            existente = None
            if modelo_str in self.CATALOGOS:
                existente = Modelo.objects.filter(pk=pk).first()
                if not existente and "nombre" in campos:
                    existente = Modelo.objects.filter(nombre=campos["nombre"]).first()

            if existente and modelo_str in self.CATALOGOS:
                saltados += 1
                continue

            # Para reportes: si ya existe por PK, saltar
            if modelo_str == "core.reporte":
                if Modelo.objects.filter(pk=pk).exists():
                    saltados += 1
                    continue

            try:
                if dry_run:
                    self.stdout.write(f"  [DRY] {modelo_str} pk={pk}")
                    creados += 1
                    continue

                with transaction.atomic():
                    # Resolver TODAS las FKs (numéricas o natural keys)
                    for campo_fk in CAMPOS_FK.get(modelo_str, []):
                        if campo_fk not in campos:
                            continue

                        valor = campos[campo_fk]
                        if valor is None:
                            continue

                        instancia = self.resolver_fk(Modelo, campo_fk, valor, mapa_reportes)
                        if instancia is not None:
                            campos[campo_fk] = instancia
                        else:
                            # Si no se pudo resolver, dejar en None para FKs opcionales
                            campo_meta = Modelo._meta.get_field(campo_fk)
                            if campo_meta.null:
                                campos[campo_fk] = None
                            else:
                                raise ValueError(
                                    f"No se pudo resolver FK {campo_fk}={valor} en {modelo_str}"
                                )

                    if modelo_str in self.CON_NUEVA_PK:
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