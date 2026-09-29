# apps/core/filters.py
from django.db.models import Q
import django_filters as filters

from .models import Reporte


class ReporteFilter(filters.FilterSet):
    desde = filters.DateFilter(field_name="fecha_creacion", lookup_expr="date__gte")
    hasta = filters.DateFilter(field_name="fecha_creacion", lookup_expr="date__lte")
    search = filters.CharFilter(method="filtrar_search", label="Búsqueda")

    class Meta:
        model = Reporte
        fields = {
            "estado": ["exact"],
            "tipo_tarea": ["exact"],
            "prioridad": ["exact"],
            "area": ["exact"],
            "tecnico_asignado": ["exact"],
        }

    def filtrar_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(codigo__icontains=value)
            | Q(descripcion__icontains=value)
            | Q(usuario_nombre__icontains=value)
            | Q(usuario_correo__icontains=value)
        )