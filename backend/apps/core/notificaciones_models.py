# apps/core/notificaciones_models.py
from django.conf import settings
from django.db import models


class Notificacion(models.Model):
    """
    Notificación interna para mostrar en la campanita del topbar.
    Se crea automáticamente cuando:
    - Se crea un nuevo reporte (notifica a admin/técnicos).
    - Cambia el estado de un reporte (notifica al usuario afectado).
    - Se asigna un técnico a un reporte (notifica al técnico).
    """
    TIPO_NUEVO_REPORTE = "nuevo_reporte"
    TIPO_CAMBIO_ESTADO = "cambio_estado"
    TIPO_ASIGNACION = "asignacion"

    TIPOS = [
        (TIPO_NUEVO_REPORTE, "Nuevo reporte"),
        (TIPO_CAMBIO_ESTADO, "Cambio de estado"),
        (TIPO_ASIGNACION, "Reporte asignado"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones",
    )
    tipo = models.CharField(max_length=20, choices=TIPOS)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField(blank=True)
    reporte = models.ForeignKey(
        "core.Reporte",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notificaciones",
    )
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"

    def __str__(self):
        return f"{self.usuario.username}: {self.titulo}"