# apps/core/notificaciones.py
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail

from .notificaciones_models import Notificacion


# ---------------------------------------------------------------------------
# Notificaciones internas (base de datos)
# ---------------------------------------------------------------------------
def notificar_nuevo_reporte_interno(reporte):
    """Notifica a admin y técnicos sobre un nuevo reporte."""
    # Destinatarios: admins + técnicos
    destinatarios = User.objects.filter(
        groups__name__in=["Administrador", "Tecnico"],
        is_active=True,
    ).exclude(id=reporte.creado_por_id).distinct()

    for user in destinatarios:
        Notificacion.objects.create(
            usuario=user,
            tipo=Notificacion.TIPO_NUEVO_REPORTE,
            titulo=f"Nuevo reporte: {reporte.codigo}",
            mensaje=(
                f"{reporte.tipo_tarea.nombre} en {reporte.area.nombre}. "
                f"Prioridad: {reporte.get_prioridad_display()}"
            ),
            reporte=reporte,
        )


def notificar_cambio_estado_interno(reporte, estado_anterior):
    """Notifica al creador y al técnico asignado del cambio de estado."""
    destinatarios = set()

    # Al creador del reporte (si no es el mismo que hizo el cambio)
    if reporte.creado_por_id:
        destinatarios.add(reporte.creado_por_id)

    # Al técnico asignado (si existe)
    if reporte.tecnico_asignado_id:
        destinatarios.add(reporte.tecnico_asignado_id)

    for user_id in destinatarios:
        Notificacion.objects.create(
            usuario_id=user_id,
            tipo=Notificacion.TIPO_CAMBIO_ESTADO,
            titulo=f"Reporte {reporte.codigo} → {reporte.get_estado_display()}",
            mensaje=f"El estado cambió de {estado_anterior} a {reporte.estado}.",
            reporte=reporte,
        )


def notificar_asignacion_interno(reporte):
    """Notifica al técnico que le asignaron un reporte."""
    if not reporte.tecnico_asignado_id:
        return
    Notificacion.objects.create(
        usuario_id=reporte.tecnico_asignado_id,
        tipo=Notificacion.TIPO_ASIGNACION,
        titulo=f"Te asignaron el reporte {reporte.codigo}",
        mensaje=(
            f"{reporte.tipo_tarea.nombre} en {reporte.area.nombre}. "
            f"Prioridad: {reporte.get_prioridad_display()}"
        ),
        reporte=reporte,
    )


# ---------------------------------------------------------------------------
# Notificaciones por correo
# ---------------------------------------------------------------------------
def notificar_nuevo_reporte_email(reporte):
    """Envía un correo cuando se crea un nuevo reporte."""
    destinatarios = getattr(settings, "NOTIFICAR_NUEVOS_REPORTES_A", [])
    if not destinatarios:
        return
    asunto = f"[Reportes TI] Nuevo reporte {reporte.codigo}"
    mensaje = (
        f"Se ha creado un nuevo reporte.\n\n"
        f"Código: {reporte.codigo}\n"
        f"Tipo: {reporte.tipo_tarea.nombre}\n"
        f"Área: {reporte.area.nombre}\n"
        f"Prioridad: {reporte.get_prioridad_display()}\n"
        f"Descripción: {reporte.descripcion[:200]}\n"
    )
    send_mail(
        asunto, mensaje, settings.DEFAULT_FROM_EMAIL, destinatarios, fail_silently=True
    )


def notificar_resolucion_email(reporte):
    """Envía un correo cuando un reporte cambia a resuelto/cerrado."""
    if not reporte.usuario_correo:
        return
    asunto = (
        f"[Reportes TI] Tu reporte {reporte.codigo} ha sido "
        f"{reporte.get_estado_display()}"
    )
    mensaje = (
        f"Hola {reporte.usuario_nombre or 'usuario'},\n\n"
        f"Tu reporte {reporte.codigo} ha cambiado al estado: "
        f"{reporte.get_estado_display()}.\n\n"
        f"Solución aplicada:\n{reporte.solucion or 'Sin registrar aún.'}\n\n"
        f"Gracias por usar el sistema de reportes técnicos."
    )
    send_mail(
        asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [reporte.usuario_correo],
        fail_silently=True,
    )


# ---------------------------------------------------------------------------
# Función unificada (hace ambas: interna y email)
# ---------------------------------------------------------------------------
def notificar_nuevo_reporte(reporte):
    notificar_nuevo_reporte_interno(reporte)
    notificar_nuevo_reporte_email(reporte)


def notificar_resolucion(reporte, estado_anterior=None):
    notificar_cambio_estado_interno(reporte, estado_anterior or "—")
    notificar_resolucion_email(reporte)


def notificar_asignacion(reporte):
    notificar_asignacion_interno(reporte)