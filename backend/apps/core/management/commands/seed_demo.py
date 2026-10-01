import os
import random
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.core.models import (
    Area, Estado, HistorialEstado, Prioridad, Reporte, TipoArea, TipoTarea, Ubicacion,
)

USUARIOS = [
    ("admin_demo", "Ana", "Administradora", settings.ROL_ADMIN),
    ("auditor_demo", "Andrés", "Auditor", settings.ROL_AUDITOR),
    ("director_demo", "Diana", "Directora", settings.ROL_DIRECTOR),
    ("tecnico1", "Carlos", "Ramírez", settings.ROL_TECNICO),
    ("tecnico2", "Laura", "Gómez", settings.ROL_TECNICO),
    ("tecnico3", "Mateo", "Pérez", settings.ROL_TECNICO),
]


class Command(BaseCommand):
    help = "Crea datos de demostración para entornos de desarrollo."

    def add_arguments(self, parser):
        parser.add_argument("--forzar", action="store_true")
        parser.add_argument("--password", default=os.environ.get("DEMO_PASSWORD", ""))

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                "seed_demo está bloqueado cuando DEBUG=False. Actívalo solo en un entorno de desarrollo."
            )

        password = options["password"] or secrets.token_urlsafe(18)
        random.seed(42)

        for nombre in settings.ROLES_DISPONIBLES:
            Group.objects.get_or_create(name=nombre)

        usuarios = {}
        for username, nombre, apellido, rol in USUARIOS:
            user, creado = User.objects.get_or_create(
                username=username,
                defaults={"first_name": nombre, "last_name": apellido, "email": f"{username}@demo.local"},
            )
            if creado:
                user.set_password(password)
                user.is_staff = rol == settings.ROL_ADMIN
                user.is_superuser = rol == settings.ROL_ADMIN
                user.save()
            user.groups.set([Group.objects.get(name=rol)])
            usuarios[username] = user

        if Reporte.objects.exists() and not options["forzar"]:
            self.stdout.write("Ya existen reportes: no se crearon reportes de ejemplo.")
        else:
            self.stdout.write(self.style.WARNING(
                "La generación de reportes demo depende de que los modelos actuales estén preparados para esos datos."
            ))

        self.stdout.write(self.style.SUCCESS(
            "Usuarios demo listos. Contraseña temporal de esta ejecución: %s" % password
        ))
