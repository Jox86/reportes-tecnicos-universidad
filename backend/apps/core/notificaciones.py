# apps/core/notificaciones.py
from django.conf import settings
from django.core.mail import send_mail


def notificar_nuevo_reporte(reporte):
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
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,
        destinatarios,
        fail_silently=True,
    )


def notificar_resolucion(reporte):
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
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,
        [reporte.usuario_correo],
        fail_silently=True,
    )