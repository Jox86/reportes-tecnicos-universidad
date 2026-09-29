# backend/scripts/crear_usuarios_prueba.py
"""
Crea usuarios de prueba (técnicos, auditores) para desarrollo.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
from django.contrib.auth.models import Group, User


def crear_usuario(username, first_name, last_name, email, rol, password="test1234"):
    user, creado = User.objects.get_or_create(
        username=username,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "is_staff": False,
            "is_superuser": False,
        },
    )
    if creado:
        user.set_password(password)
        user.save()
        print(f"  ✓ Creado: {username} ({rol}) - contraseña: {password}")
    else:
        print(f"  · Ya existe: {username}")

    # Asignar rol (grupo)
    grupo, _ = Group.objects.get_or_create(name=rol)
    user.groups.add(grupo)

    return user


def main():
    print("=== Creando usuarios de prueba ===\n")

    print("--- Técnicos ---")
    crear_usuario("tecnico1", "Carlos", "Ramírez", "carlos.ramirez@universidad.edu", settings.ROL_TECNICO)
    crear_usuario("tecnico2", "María", "González", "maria.gonzalez@universidad.edu", settings.ROL_TECNICO)
    crear_usuario("tecnico3", "Juan", "Pérez", "juan.perez@universidad.edu", settings.ROL_TECNICO)

    print("\n--- Auditores ---")
    crear_usuario("auditor1", "Ana", "Martínez", "ana.martinez@universidad.edu", settings.ROL_AUDITOR)
    crear_usuario("auditor2", "Luis", "Fernández", "luis.fernandez@universidad.edu", settings.ROL_AUDITOR)

    print("\n--- Administrador (si no existe) ---")
    crear_usuario("admin2", "Pedro", "López", "pedro.lopez@universidad.edu", settings.ROL_ADMIN)

    print("\n=== ¡Usuarios creados! ===")
    print("\nCredenciales para probar:")
    print("  Técnicos:   tecnico1 / tecnico2 / tecnico3  →  test1234")
    print("  Auditores:  auditor1 / auditor2              →  test1234")
    print("  Admin:      admin2                           →  test1234")


if __name__ == "__main__":
    main()