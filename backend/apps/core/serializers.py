# apps/core/serializers.py
from rest_framework import serializers

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


# --- Catálogos ---
class TipoAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoArea
        fields = ["id", "nombre", "descripcion"]


class AreaSerializer(serializers.ModelSerializer):
    tipo_area_nombre = serializers.CharField(source="tipo_area.nombre", read_only=True)

    class Meta:
        model = Area
        fields = ["id", "nombre", "tipo_area", "tipo_area_nombre", "responsable", "activo"]


class UbicacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ubicacion
        fields = ["id", "nombre", "area", "edificio", "piso", "referencia"]


class TipoTareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoTarea
        fields = ["id", "codigo", "nombre", "activo"]


# --- Equipos y archivos ---
class EquipoReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipoReporte
        fields = ["id", "codigo_activo", "marca", "modelo", "serie"]


class ArchivoReporteSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ArchivoReporte
        fields = ["id", "nombre", "url", "fecha_subida"]

    def get_url(self, obj):
        request = self.context.get("request")
        if request and obj.archivo:
            return request.build_absolute_uri(obj.archivo.url)
        return obj.archivo.url if obj.archivo else None


class HistorialEstadoSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = HistorialEstado
        fields = ["id", "estado_anterior", "estado_nuevo", "comentario", "usuario_nombre", "fecha"]

    def get_usuario_nombre(self, obj):
        if obj.usuario:
            return obj.usuario.get_full_name() or obj.usuario.username
        return "Sistema"


# --- Reporte completo ---
class ReporteSerializer(serializers.ModelSerializer):
    tipo_tarea_nombre = serializers.CharField(source="tipo_tarea.nombre", read_only=True)
    area_nombre = serializers.CharField(source="area.nombre", read_only=True)
    tecnico_nombre = serializers.SerializerMethodField()
    creado_por_nombre = serializers.SerializerMethodField()
    equipos = EquipoReporteSerializer(many=True, required=False)
    archivos = ArchivoReporteSerializer(many=True, read_only=True)
    historial = HistorialEstadoSerializer(many=True, read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    prioridad_display = serializers.CharField(source="get_prioridad_display", read_only=True)
    tiempo_resolucion_horas = serializers.FloatField(read_only=True)

    class Meta:
        model = Reporte
        fields = [
            "id", "codigo", "tipo_tarea", "tipo_tarea_nombre",
            "descripcion", "solucion",
            "area", "area_nombre", "ubicacion",
            "usuario_nombre", "usuario_correo", "usuario_cargo",
            "prioridad", "prioridad_display", "estado", "estado_display",
            "creado_por", "creado_por_nombre",
            "tecnico_asignado", "tecnico_nombre",
            "fecha_creacion", "fecha_actualizacion", "fecha_resolucion",
            "tiempo_resolucion_horas",
            "equipos", "archivos", "historial",
        ]
        read_only_fields = ["codigo", "creado_por", "fecha_creacion", "fecha_actualizacion", "fecha_resolucion"]

    def get_tecnico_nombre(self, obj):
        return obj.tecnico_nombre

    def get_creado_por_nombre(self, obj):
        return obj.creado_por_nombre

    def create(self, validated_data):
        equipos_data = validated_data.pop("equipos", [])
        validated_data["creado_por"] = self.context["request"].user
        reporte = Reporte.objects.create(**validated_data)
        for eq_data in equipos_data:
            EquipoReporte.objects.create(reporte=reporte, **eq_data)
        return reporte

    def update(self, instance, validated_data):
        equipos_data = validated_data.pop("equipos", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if equipos_data is not None:
            instance.equipos.all().delete()
            for eq_data in equipos_data:
                EquipoReporte.objects.create(reporte=instance, **eq_data)
        return instance


class ReporteListSerializer(serializers.ModelSerializer):
    """Versión ligera para listados."""
    tipo_tarea_display = serializers.CharField(source="tipo_tarea.nombre", read_only=True)
    area_nombre = serializers.CharField(source="area.nombre", read_only=True)
    tecnico_nombre = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    prioridad_display = serializers.CharField(source="get_prioridad_display", read_only=True)

    class Meta:
        model = Reporte
        fields = [
            "id", "codigo", "tipo_tarea", "tipo_tarea_display",
            "area", "area_nombre", "ubicacion",
            "prioridad", "prioridad_display", "estado", "estado_display",
            "tecnico_asignado", "tecnico_nombre",
            "fecha_creacion", "fecha_resolucion", "tiempo_resolucion_horas",
        ]

    def get_tecnico_nombre(self, obj):
        return obj.tecnico_nombre