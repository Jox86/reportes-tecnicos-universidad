# apps/core/admin.py
from django.contrib import admin

from .models import (
    ArchivoReporte,
    Area,
    EquipoReporte,
    HistorialEstado,
    Reporte,
    TipoArea,
    TipoTarea,
    Ubicacion,
)


# ---------------------------------------------------------------------------
# Catálogos
# ---------------------------------------------------------------------------
@admin.register(TipoArea)
class TipoAreaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo_area", "responsable", "activo")
    list_filter = ("tipo_area", "activo")
    search_fields = ("nombre", "responsable")


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "area", "edificio", "piso")
    list_filter = ("area",)
    search_fields = ("nombre", "edificio")


@admin.register(TipoTarea)
class TipoTareaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "activo", "creado_por", "fecha_creacion")
    list_filter = ("activo",)
    search_fields = ("nombre", "codigo")


# ---------------------------------------------------------------------------
# Reportes
# ---------------------------------------------------------------------------
class EquipoReporteInline(admin.TabularInline):
    model = EquipoReporte
    extra = 0


class ArchivoReporteInline(admin.TabularInline):
    model = ArchivoReporte
    extra = 0
    readonly_fields = ("fecha_subida",)


class HistorialEstadoInline(admin.TabularInline):
    model = HistorialEstado
    extra = 0
    readonly_fields = ("fecha",)
    can_delete = False


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "tipo_tarea",
        "area",
        "prioridad",
        "estado",
        "tecnico_asignado",
        "fecha_creacion",
    )
    list_filter = ("estado", "prioridad", "area", "tipo_tarea")
    search_fields = ("codigo", "descripcion", "usuario_nombre", "usuario_correo")
    readonly_fields = ("codigo", "fecha_creacion", "fecha_actualizacion", "fecha_resolucion")
    inlines = [EquipoReporteInline, ArchivoReporteInline, HistorialEstadoInline]
    date_hierarchy = "fecha_creacion"
    ordering = ("-fecha_creacion",)

    fieldsets = (
        ("Identificación", {
            "fields": ("codigo", "tipo_tarea", "prioridad", "estado")
        }),
        ("Ubicación", {
            "fields": ("area", "ubicacion")
        }),
        ("Usuario afectado", {
            "fields": ("usuario_nombre", "usuario_correo", "usuario_cargo")
        }),
        ("Descripción y solución", {
            "fields": ("descripcion", "solucion")
        }),
        ("Asignación", {
            "fields": ("creado_por", "tecnico_asignado")
        }),
        ("Fechas", {
            "fields": ("fecha_creacion", "fecha_actualizacion", "fecha_resolucion")
        }),
    )


@admin.register(EquipoReporte)
class EquipoReporteAdmin(admin.ModelAdmin):
    list_display = ("codigo_activo", "marca", "modelo", "serie", "reporte")
    search_fields = ("codigo_activo", "serie", "reporte__codigo")


@admin.register(ArchivoReporte)
class ArchivoReporteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "reporte", "subido_por", "fecha_subida")
    search_fields = ("nombre", "reporte__codigo")


@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    list_display = ("reporte", "estado_anterior", "estado_nuevo", "usuario", "fecha")
    list_filter = ("estado_nuevo",)
    search_fields = ("reporte__codigo", "comentario")


from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "tipo", "titulo", "leida", "fecha")
    list_filter = ("tipo", "leida", "fecha")
    search_fields = ("usuario__username", "titulo", "mensaje")
    date_hierarchy = "fecha"