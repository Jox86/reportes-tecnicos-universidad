import os
import random
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import (
    Area,
    Estado,
    HistorialEstado,
    Prioridad,
    Reporte,
    TipoArea,
    TipoTarea,
    Ubicacion,
)

PASSWORD = os.environ.get("DEMO_PASSWORD") or secrets.token_urlsafe(18)

USUARIOS = [
    ("admin_demo", "Ana", "Administradora", settings.ROL_ADMIN),
    ("auditor_demo", "Andrés", "Auditor", settings.ROL_AUDITOR),
    ("director_demo", "Diana", "Directora", settings.ROL_DIRECTOR),
    ("tecnico1", "Carlos", "Ramírez", settings.ROL_TECNICO),
    ("tecnico2", "Laura", "Gómez", settings.ROL_TECNICO),
    ("tecnico3", "Mateo", "Pérez", settings.ROL_TECNICO),
]

CATALOGO = {
    "Académica": {
        "Facultad de Ingeniería": ["Sala de cómputo 101", "Decanatura"],
        "Facultad de Ciencias": ["Laboratorio de física", "Sala de profesores"],
    },
    "Administrativa": {
        "Rectoría": ["Oficina de rectoría", "Secretaría general"],
        "Bienestar Universitario": ["Recepción", "Consultorio médico"],
    },
    "Biblioteca": {
        "Biblioteca Central": ["Sala de consulta", "Módulo de préstamos"],
    },
    "Laboratorio": {
        "Laboratorio de Cómputo": ["Sala A", "Sala B"],
    },
}

PLANTILLAS = {
    TipoTarea.ACTIVOS_FIJOS: ("Inventario y etiquetado de equipos", "Levantamiento y etiquetado de activos fijos del área."),
    TipoTarea.REPARACION_HARDWARE: ("Equipo que no enciende", "El equipo no enciende; se sospecha falla en la fuente de poder."),
    TipoTarea.ACTUALIZACION_SISTEMA: ("Actualización del sistema operativo", "Actualización de Windows y controladores pendientes."),
    TipoTarea.RECUPERACION_CUENTAS: ("Recuperación de contraseña institucional", "El usuario no puede ingresar a su cuenta institucional."),
    TipoTarea.MANTENIMIENTO_PREVENTIVO: ("Mantenimiento preventivo de equipos", "Limpieza interna y revisión general de los equipos."),
    TipoTarea.SOPORTE_RED: ("Sin conexión a la red", "El punto de red no entrega conectividad."),
    TipoTarea.INSTALACION_SOFTWARE: ("Instalación de software académico", "Instalación y licenciamiento del software solicitado."),
}

USUARIOS_AFECTADOS = ["María Torres", "Juan Herrera", "Sofía Castro", "Pedro Núñez", "Lucía Ortiz", "Andrés Vega", "Paula Rojas"]
MARCAS = [("Dell", "OptiPlex 7010"), ("HP", "ProDesk 400"), ("Lenovo", "ThinkCentre M70")]
CAMINO_ESTADOS = [Estado.PENDIENTE, Estado.EN_PROCESO, Estado.RESUELTO, Estado.CERRADO]


class Command(BaseCommand):
    help = "Crea datos de demostración (usuarios por rol, catálogos y reportes) para probar la app sin AD."

    def add_arguments(self, parser):
        parser.add_argument(
            "--forzar",
            action="store_true",
            help="Crear reportes de ejemplo aunque ya existan reportes.",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_demo está bloqueado cuando DEBUG=False. Úsalo solo en desarrollo.")
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
                user.set_password(PASSWORD)
            if rol == settings.ROL_ADMIN:
                user.is_staff = True
                user.is_superuser = True
            user.save()
            user.groups.set([Group.objects.get(name=rol)])
            usuarios[username] = user

        areas = []
        for tipo_nombre, areas_dict in CATALOGO.items():
            tipo, _ = TipoArea.objects.get_or_create(nombre=tipo_nombre)
            for area_nombre, ubicaciones in areas_dict.items():
                area, _ = Area.objects.get_or_create(nombre=area_nombre, defaults={"tipo_area": tipo})
                for nombre_ubicacion in ubicaciones:
                    Ubicacion.objects.get_or_create(nombre=nombre_ubicacion, area=area)
                areas.append(area)

        if Reporte.objects.exists() and not options["forzar"]:
            self.stdout.write("Ya existen reportes: no se crearon reportes de ejemplo (usa --forzar para agregar más).")
        else:
            tecnicos = [usuarios["tecnico1"], usuarios["tecnico2"], usuarios["tecnico3"]]
            self._crear_reportes(areas, tecnicos)

        self.stdout.write(self.style.SUCCESS("\nDatos de demostración listos. Usuarios (contraseña para todos: %s):" % PASSWORD))
        for username, _, _, rol in USUARIOS:
            self.stdout.write(f"  {username:<15} → {rol}")

    def _crear_reportes(self, areas, tecnicos, cantidad=45):
        ahora = timezone.now()
        for _ in range(cantidad):
            dias = random.randint(0, 180)
            creado = ahora - timedelta(days=dias, hours=random.randint(0, 8))
            tipo = random.choice(list(PLANTILLAS))
            titulo, descripcion = PLANTILLAS[tipo]
            area = random.choice(areas)
            ubicacion = random.choice(list(area.ubicaciones.all()))
            tecnico = random.choice(tecnicos)
            marca, modelo = random.choice(MARCAS)
            afectado = random.choice(USUARIOS_AFECTADOS)

            if dias > 10:
                estado = random.choices(
                    [Estado.RESUELTO, Estado.CERRADO, Estado.EN_PROCESO, Estado.PENDIENTE], [50, 35, 8, 7]
                )[0]
            else:
                estado = random.choices([Estado.PENDIENTE, Estado.EN_PROCESO, Estado.RESUELTO], [40, 35, 25])[0]

            hasta = CAMINO_ESTADOS.index(estado)
            fechas = [creado]
            for _paso in range(hasta):
                fechas.append(min(fechas[-1] + timedelta(hours=random.randint(1, 24)), ahora))

            reporte = Reporte.objects.create(
                tipo_tarea=tipo,
                titulo=titulo,
                descripcion=descripcion,
                solucion="Se realizó el procedimiento y se verificó el correcto funcionamiento." if hasta >= 2 else "",
                area=area,
                ubicacion=ubicacion,
                usuario_nombre=afectado,
                usuario_correo=f"{afectado.split()[0].lower()}@demo.local",
                usuario_cargo="Docente",
                codigo_activo=f"AF-{random.randint(1000, 9999)}",
                equipo_marca=marca,
                equipo_modelo=modelo,
                equipo_serie=f"SN{random.randint(100000, 999999)}",
                prioridad=random.choice(list(Prioridad.values)),
                estado=estado,
                creado_por=tecnico,
                tecnico_asignado=tecnico,
            )

            # auto_now/auto_now_add fijan la fecha actual; se reescriben para simular historial real
            Reporte.objects.filter(pk=reporte.pk).update(
                fecha_creacion=creado,
                fecha_actualizacion=fechas[-1],
                fecha_resolucion=fechas[2] if hasta >= 2 else None,
            )

            for i in range(hasta + 1):
                registro = HistorialEstado.objects.create(
                    reporte=reporte,
                    estado_anterior="" if i == 0 else CAMINO_ESTADOS[i - 1],
                    estado_nuevo=CAMINO_ESTADOS[i],
                    comentario="Reporte creado" if i == 0 else "Cambio de estado (datos de demostración)",
                    usuario=tecnico,
                )
                HistorialEstado.objects.filter(pk=registro.pk).update(fecha=fechas[i])

        self.stdout.write(f"{cantidad} reportes de ejemplo creados.")
