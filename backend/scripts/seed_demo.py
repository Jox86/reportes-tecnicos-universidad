# backend/scripts/seed_demo.py
"""
Script para crear datos de prueba:
- Usuarios (técnicos, auditores)
- Áreas y tipos de área
- Ubicaciones
- Tipos de tarea
- Reportes de ejemplo
- Asignaciones y cambios de estado

Uso:
    python manage.py shell < scripts/seed_demo.py
    o
    python scripts/seed_demo.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import Group, User
from django.utils import timezone

from apps.core.models import (
    Area,
    ArchivoReporte,
    EquipoReporte,
    Estado,
    HistorialEstado,
    Prioridad,
    Reporte,
    TipoArea,
    TipoTarea,
    Ubicacion,
)


# ===========================================================================
# 1. USUARIOS
# ===========================================================================
def crear_usuarios():
    print("\n=== Creando usuarios ===")

    # Técnicos
    tecnicos = [
        ("tecnico1", "Carlos", "Ramírez", "carlos.ramirez@universidad.edu"),
        ("tecnico2", "María", "González", "maria.gonzalez@universidad.edu"),
        ("tecnico3", "Juan", "Pérez", "juan.perez@universidad.edu"),
    ]
    for username, first, last, email in tecnicos:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"first_name": first, "last_name": last, "email": email},
        )
        if created:
            user.set_password("test1234")
            user.save()
            print(f"  ✓ Técnico creado: {username} / test1234")
        else:
            print(f"  · Ya existe: {username}")
        user.groups.add(Group.objects.get_or_create(name="Tecnico")[0])

    # Auditores
    auditores = [
        ("auditor1", "Ana", "Martínez", "ana.martinez@universidad.edu"),
        ("auditor2", "Luis", "Fernández", "luis.fernandez@universidad.edu"),
    ]
    for username, first, last, email in auditores:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"first_name": first, "last_name": last, "email": email},
        )
        if created:
            user.set_password("test1234")
            user.save()
            print(f"  ✓ Auditor creado: {username} / test1234")
        else:
            print(f"  · Ya existe: {username}")
        user.groups.add(Group.objects.get_or_create(name="Auditor")[0])

    print(f"\n  Total usuarios: {User.objects.count()}")


# ===========================================================================
# 2. CATÁLOGOS
# ===========================================================================
def crear_catalogos():
    print("\n=== Creando catálogos ===")

    # Tipos de área
    tipos_area = [
        ("Académica", "Áreas de docencia e investigación"),
        ("Administrativa", "Áreas de gestión administrativa"),
        ("Servicios", "Servicios generales"),
        ("TI", "Tecnologías de la información"),
    ]
    for nombre, descripcion in tipos_area:
        obj, created = TipoArea.objects.get_or_create(
            nombre=nombre, defaults={"descripcion": descripcion}
        )
        print(f"  {'✓' if created else '·'} TipoArea: {nombre}")

    # Áreas
    tipo_ti = TipoArea.objects.get(nombre="TI")
    tipo_academica = TipoArea.objects.get(nombre="Académica")
    tipo_admin = TipoArea.objects.get(nombre="Administrativa")

    areas = [
        ("Sistemas", tipo_ti),
        ("Redes y Comunicaciones", tipo_ti),
        ("Biblioteca", tipo_academica),
        ("Registro Académico", tipo_academica),
        ("Recursos Humanos", tipo_admin),
        ("Contabilidad", tipo_admin),
    ]
    for nombre, tipo in areas:
        obj, created = Area.objects.get_or_create(
            nombre=nombre, defaults={"tipo_area": tipo, "activo": True}
        )
        print(f"  {'✓' if created else '·'} Área: {nombre}")

    # Ubicaciones
    sistemas = Area.objects.get(nombre="Sistemas")
    redes = Area.objects.get(nombre="Redes y Comunicaciones")
    biblioteca = Area.objects.get(nombre="Biblioteca")

    ubicaciones = [
        ("Oficina Sistemas", sistemas, "Edificio A", "Piso 2", "Ala norte"),
        ("Sala de Servidores", sistemas, "Edificio A", "Piso 1", "Sótano"),
        ("Laboratorio Redes", redes, "Edificio B", "Piso 3", "Ala sur"),
        ("Sala de Lectura", biblioteca, "Edificio Central", "Piso 1", "Entrada principal"),
    ]
    for nombre, area, edificio, piso, referencia in ubicaciones:
        obj, created = Ubicacion.objects.get_or_create(
            nombre=nombre,
            area=area,
            defaults={"edificio": edificio, "piso": piso, "referencia": referencia},
        )
        print(f"  {'✓' if created else '·'} Ubicación: {nombre}")

    # Tipos de tarea
    tipos_tarea = [
        ("activos_fijos", "Gestión de activos fijos"),
        ("reparacion_hardware", "Reparación de hardware"),
        ("actualizacion_sistema", "Actualización de sistema"),
        ("recuperacion_cuentas", "Recuperación de cuentas"),
        ("mantenimiento_preventivo", "Mantenimiento preventivo"),
        ("soporte_red", "Soporte de red"),
        ("instalacion_software", "Instalación de software"),
    ]
    for codigo, nombre in tipos_tarea:
        obj, created = TipoTarea.objects.get_or_create(
            codigo=codigo, defaults={"nombre": nombre}
        )
        print(f"  {'✓' if created else '·'} TipoTarea: {nombre}")


# ===========================================================================
# 3. REPORTES DE PRUEBA
# ===========================================================================
def crear_reportes():
    print("\n=== Creando reportes de prueba ===")

    admin = User.objects.filter(is_superuser=True).first()
    tecnico1 = User.objects.get(username="tecnico1")
    tecnico2 = User.objects.get(username="tecnico2")

    sistemas = Area.objects.get(nombre="Sistemas")
    redes = Area.objects.get(nombre="Redes y Comunicaciones")
    biblioteca = Area.objects.get(nombre="Biblioteca")

    tipo_hardware = TipoTarea.objects.get(codigo="reparacion_hardware")
    tipo_red = TipoTarea.objects.get(codigo="soporte_red")
    tipo_software = TipoTarea.objects.get(codigo="instalacion_software")
    tipo_activos = TipoTarea.objects.get(codigo="activos_fijos")

    reportes_data = [
        {
            "tipo_tarea": tipo_hardware,
            "descripcion": "El computador de la sala de lectura no enciende. Se revisó el cable de poder y parece estar en buen estado, pero no responde al botón de encendido.",
            "area": biblioteca,
            "ubicacion": "Sala de Lectura - PC #5",
            "usuario_nombre": "María López",
            "usuario_correo": "maria.lopez@universidad.edu",
            "usuario_cargo": "Bibliotecaria",
            "prioridad": Prioridad.ALTA,
            "estado": Estado.RESUELTO,
            "solucion": "Se reemplazó la fuente de poder. El equipo ya enciende correctamente.",
            "tecnico": tecnico1,
            "equipos": [
                {"codigo_activo": "ACT-001", "marca": "Dell", "modelo": "OptiPlex 3080", "serie": "SN-12345"}
            ],
        },
        {
            "tipo_tarea": tipo_red,
            "descripcion": "No hay conexión a internet en el laboratorio de redes. Los estudiantes no pueden acceder a los recursos en línea.",
            "area": redes,
            "ubicacion": "Laboratorio Redes - Switch principal",
            "usuario_nombre": "Pedro Sánchez",
            "usuario_correo": "pedro.sanchez@universidad.edu",
            "usuario_cargo": "Docente",
            "prioridad": Prioridad.CRITICA,
            "estado": Estado.EN_PROCESO,
            "tecnico": tecnico2,
            "equipos": [
                {"codigo_activo": "SW-001", "marca": "Cisco", "modelo": "Catalyst 2960", "serie": "SW-98765"}
            ],
        },
        {
            "tipo_tarea": tipo_software,
            "descripcion": "Instalar Microsoft Office en los 10 computadores nuevos del laboratorio de cómputo.",
            "area": sistemas,
            "ubicacion": "Laboratorio de Cómputo",
            "usuario_nombre": "Laura Torres",
            "usuario_correo": "laura.torres@universidad.edu",
            "usuario_cargo": "Coordinadora",
            "prioridad": Prioridad.MEDIA,
            "estado": Estado.PENDIENTE,
            "tecnico": None,
            "equipos": [
                {"codigo_activo": f"PC-{i:03d}", "marca": "HP", "modelo": "ProDesk 400", "serie": f"HP-{i:05d}"}
                for i in range(1, 4)  # 3 equipos de ejemplo
            ],
        },
        {
            "tipo_tarea": tipo_activos,
            "descripcion": "Registrar 20 equipos nuevos en el inventario de activos fijos.",
            "area": sistemas,
            "ubicacion": "Oficina Sistemas",
            "usuario_nombre": "Carlos Ruiz",
            "usuario_correo": "carlos.ruiz@universidad.edu",
            "usuario_cargo": "Jefe de Sistemas",
            "prioridad": Prioridad.BAJA,
            "estado": Estado.CERRADO,
            "solucion": "Se registraron todos los equipos con sus respectivos códigos de activo.",
            "tecnico": tecnico1,
            "equipos": [],
        },
        {
            "tipo_tarea": tipo_hardware,
            "descripcion": "El proyector del aula 302 no muestra imagen. Se probó con otro cable HDMI y sigue igual.",
            "area": biblioteca,
            "ubicacion": "Aula 302",
            "usuario_nombre": "Docente Anónimo",
            "usuario_correo": "",
            "usuario_cargo": "",
            "prioridad": Prioridad.MEDIA,
            "estado": Estado.PENDIENTE,
            "tecnico": None,
            "equipos": [
                {"codigo_activo": "PROY-001", "marca": "Epson", "modelo": "PowerLite X49", "serie": "EP-X49-001"}
            ],
        },
    ]

    for i, data in enumerate(reportes_data, 1):
        # Verificar si ya existe un reporte similar
        if Reporte.objects.filter(descripcion=data["descripcion"]).exists():
            print(f"  · Reporte {i} ya existe, saltando")
            continue

        equipos_data = data.pop("equipos", [])
        tecnico = data.pop("tecnico", None)

        reporte = Reporte.objects.create(
            creado_por=admin,
            tecnico_asignado=tecnico,
            fecha_resolucion=timezone.now() if data["estado"] in [Estado.RESUELTO, Estado.CERRADO] else None,
            **data,
        )

        # Crear equipos
        for eq in equipos_data:
            EquipoReporte.objects.create(reporte=reporte, **eq)

        # Crear historial inicial
        HistorialEstado.objects.create(
            reporte=reporte,
            estado_anterior="",
            estado_nuevo=Estado.PENDIENTE,
            comentario="Reporte creado",
            usuario=admin,
        )

        # Si tiene estado diferente a pendiente, agregar historial
        if data["estado"] != Estado.PENDIENTE:
            HistorialEstado.objects.create(
                reporte=reporte,
                estado_anterior=Estado.PENDIENTE,
                estado_nuevo=data["estado"],
                comentario="Cambio de estado",
                usuario=tecnico or admin,
            )

        print(f"  ✓ Reporte creado: {reporte.codigo} ({data['estado']})")

    print(f"\n  Total reportes: {Reporte.objects.count()}")


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    print("=" * 60)
    print("  CARGANDO DATOS DE PRUEBA")
    print("=" * 60)

    crear_usuarios()
    crear_catalogos()
    crear_reportes()

    print("\n" + "=" * 60)
    print("  ¡DATOS DE PRUEBA CARGADOS!")
    print("=" * 60)
    print("\nUsuarios de prueba:")
    print("  Técnicos:  tecnico1 / tecnico2 / tecnico3  →  test1234")
    print("  Auditores: auditor1 / auditor2              →  test1234")
    print("  Admin:     fox6 (tu superusuario)")


if __name__ == "__main__":
    main()