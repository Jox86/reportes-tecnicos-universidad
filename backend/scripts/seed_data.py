# backend/scripts/seed_data.py
"""
Script para cargar datos iniciales del sistema:
- Roles (Administrador, Auditor, Tecnico)
- Tipos de tarea
- Tipos de área
"""
import os
import sys
from pathlib import Path

# Asegurar que el directorio backend esté en el path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
from django.contrib.auth.models import Group
from apps.core.models import TipoArea, TipoTarea


def crear_roles():
    print("=== Creando roles ===")
    for rol in settings.ROLES_DISPONIBLES:
        obj, creado = Group.objects.get_or_create(name=rol)
        print(f"  {'✓ Creado' if creado else '· Ya existe'}: {rol}")


def crear_tipos_tarea():
    print("\n=== Creando tipos de tarea ===")
    tipos = [
        ("activos_fijos", "Gestión de activos fijos"),
        ("reparacion_hardware", "Reparación de hardware"),
        ("actualizacion_sistema", "Actualización de sistema"),
        ("recuperacion_cuentas", "Recuperación de cuentas"),
        ("mantenimiento_preventivo", "Mantenimiento preventivo"),
        ("soporte_red", "Soporte de red"),
        ("instalacion_software", "Instalación de software"),
    ]
    for codigo, nombre in tipos:
        obj, creado = TipoTarea.objects.get_or_create(
            codigo=codigo, defaults={"nombre": nombre}
        )
        print(f"  {'✓ Creado' if creado else '· Ya existe'}: {nombre}")


def crear_tipos_area():
    print("\n=== Creando tipos de área ===")
    tipos = [
        ("Académica", "Áreas relacionadas con docencia e investigación"),
        ("Administrativa", "Áreas administrativas y de gestión"),
        ("Servicios", "Áreas de servicios generales"),
        ("TI", "Tecnologías de la información"),
    ]
    for nombre, descripcion in tipos:
        obj, creado = TipoArea.objects.get_or_create(
            nombre=nombre, defaults={"descripcion": descripcion}
        )
        print(f"  {'✓ Creado' if creado else '· Ya existe'}: {nombre}")


if __name__ == "__main__":
    print("=========================================")
    print("  Cargando datos iniciales del sistema")
    print("=========================================\n")
    crear_roles()
    crear_tipos_tarea()
    crear_tipos_area()
    print("\n=========================================")
    print("  ¡Datos iniciales cargados con éxito!")
    print("=========================================")