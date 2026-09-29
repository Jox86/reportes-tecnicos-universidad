from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea los grupos/roles base del sistema: Administrador, Auditor, Director, Tecnico."

    def handle(self, *args, **options):
        for nombre in settings.ROLES_DISPONIBLES:
            _, creado = Group.objects.get_or_create(name=nombre)
            if creado:
                self.stdout.write(self.style.SUCCESS(f"Grupo creado: {nombre}"))
            else:
                self.stdout.write(f"Ya existía: {nombre}")
        self.stdout.write(self.style.SUCCESS("Roles listos. Asigna usuarios a estos grupos desde /admin/."))
