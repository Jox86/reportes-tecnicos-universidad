# apps/core/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone


# ---------------------------------------------------------------------------
# Catálogos base
# ---------------------------------------------------------------------------
class TipoArea(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Tipo de área"
        verbose_name_plural = "Tipos de área"

    def __str__(self):
        return self.nombre


class Area(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    tipo_area = models.ForeignKey(TipoArea, on_delete=models.PROTECT, related_name="areas")
    responsable = models.CharField(max_length=150, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Ubicacion(models.Model):
    nombre = models.CharField(max_length=150)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="ubicaciones")
    edificio = models.CharField(max_length=100, blank=True)
    piso = models.CharField(max_length=50, blank=True)
    referencia = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["area__nombre", "nombre"]
        unique_together = ("nombre", "area")

    def __str__(self):
        return f"{self.nombre} ({self.area.nombre})"


# ---------------------------------------------------------------------------
# Tipo de tarea (dinámico: se pueden agregar desde el frontend)
# ---------------------------------------------------------------------------
class TipoTarea(models.Model):
    """Tipos de tarea configurables. Los técnicos pueden crear nuevos."""
    codigo = models.SlugField(max_length=50, unique=True)
    nombre = models.CharField(max_length=150)
    activo = models.BooleanField(default=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tipos_tarea_creados",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Tipo de tarea"
        verbose_name_plural = "Tipos de tarea"

    def __str__(self):
        return self.nombre


class Prioridad(models.TextChoices):
    BAJA = "baja", "Baja"
    MEDIA = "media", "Media"
    ALTA = "alta", "Alta"
    CRITICA = "critica", "Crítica"


class Estado(models.TextChoices):
    PENDIENTE = "pendiente", "Pendiente"
    EN_PROCESO = "en_proceso", "En proceso"
    RESUELTO = "resuelto", "Resuelto"
    CERRADO = "cerrado", "Cerrado"


# ---------------------------------------------------------------------------
# Reporte principal
# ---------------------------------------------------------------------------
class Reporte(models.Model):
    codigo = models.CharField(max_length=20, unique=True, editable=False)

    tipo_tarea = models.ForeignKey(
        TipoTarea, on_delete=models.PROTECT, related_name="reportes"
    )
    descripcion = models.TextField()
    solucion = models.TextField(blank=True)

    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="reportes")
    ubicacion = models.CharField("Ubicación", max_length=255, blank=True)

    usuario_nombre = models.CharField("Usuario afectado", max_length=150, blank=True)
    usuario_correo = models.EmailField("Correo del usuario", blank=True)
    usuario_cargo = models.CharField("Cargo / dependencia", max_length=150, blank=True)

    prioridad = models.CharField(max_length=10, choices=Prioridad.choices, default=Prioridad.MEDIA)
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.PENDIENTE)

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reportes_creados"
    )
    tecnico_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reportes_asignados",
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.codigo} · {self.tipo_tarea.nombre}"

    def save(self, *args, **kwargs):
        if not self.codigo:
            year = timezone.now().year
            prefijo = f"RPT-{year}-"
            ultimo = Reporte.objects.filter(codigo__startswith=prefijo).order_by("-codigo").first()
            siguiente = int(ultimo.codigo.split("-")[-1]) + 1 if ultimo else 1
            self.codigo = f"{prefijo}{siguiente:04d}"
        super().save(*args, **kwargs)

    @property
    def tiempo_resolucion_horas(self):
        if self.fecha_resolucion:
            delta = self.fecha_resolucion - self.fecha_creacion
            return round(delta.total_seconds() / 3600, 1)
        return None

    @property
    def tecnico_nombre(self):
        if self.tecnico_asignado:
            return self.tecnico_asignado.get_full_name() or self.tecnico_asignado.username
        return None

    @property
    def creado_por_nombre(self):
        return self.creado_por.get_full_name() or self.creado_por.username


# ---------------------------------------------------------------------------
# Equipos (varios por reporte)
# ---------------------------------------------------------------------------
class EquipoReporte(models.Model):
    reporte = models.ForeignKey(Reporte, on_delete=models.CASCADE, related_name="equipos")
    codigo_activo = models.CharField("Código de activo", max_length=100, blank=True)
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    serie = models.CharField("Número de serie", max_length=100, blank=True)

    class Meta:
        verbose_name = "Equipo del reporte"
        verbose_name_plural = "Equipos del reporte"

    def __str__(self):
        return f"{self.codigo_activo or 'Equipo'} - {self.marca} {self.modelo}"


# ---------------------------------------------------------------------------
# Archivos adjuntos
# ---------------------------------------------------------------------------
class ArchivoReporte(models.Model):
    reporte = models.ForeignKey(Reporte, on_delete=models.CASCADE, related_name="archivos")
    archivo = models.FileField(upload_to="reportes/archivos/%Y/%m/")
    nombre = models.CharField(max_length=255, blank=True)
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="archivos_subidos",
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_subida"]

    def __str__(self):
        return self.nombre or self.archivo.name


# ---------------------------------------------------------------------------
# Historial de cambios
# ---------------------------------------------------------------------------
class HistorialEstado(models.Model):
    reporte = models.ForeignKey(Reporte, on_delete=models.CASCADE, related_name="historial")
    estado_anterior = models.CharField(max_length=15, choices=Estado.choices, blank=True)
    estado_nuevo = models.CharField(max_length=15, choices=Estado.choices)
    comentario = models.TextField(blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Historial de estado"
        verbose_name_plural = "Historial de estados"

    def __str__(self):
        return f"{self.reporte.codigo}: {self.estado_anterior} -> {self.estado_nuevo}"


# ---------------------------------------------------------------------------
# Notificaciones internas
# ---------------------------------------------------------------------------
class Notificacion(models.Model):
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