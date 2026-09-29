# apps/stats/views.py
from datetime import timedelta

from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import Estado, Reporte
from apps.core.permissions import reportes_visibles_para


def _queryset_base(request):
    qs = Reporte.objects.all()
    qs = reportes_visibles_para(request.user, qs)
    desde = request.GET.get("desde")
    hasta = request.GET.get("hasta")
    if desde:
        qs = qs.filter(fecha_creacion__date__gte=desde)
    if hasta:
        qs = qs.filter(fecha_creacion__date__lte=hasta)
    return qs


class ResumenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = _queryset_base(request)
        total = qs.count()
        por_estado = {row["estado"]: row["total"] for row in qs.values("estado").annotate(total=Count("id"))}

        resueltos_qs = qs.filter(fecha_resolucion__isnull=False).annotate(
            duracion=ExpressionWrapper(F("fecha_resolucion") - F("fecha_creacion"), output_field=DurationField())
        )
        promedio = resueltos_qs.aggregate(promedio=Avg("duracion"))["promedio"]
        promedio_horas = round(promedio.total_seconds() / 3600, 1) if promedio else None

        vencidos = qs.filter(
            estado__in=[Estado.PENDIENTE, Estado.EN_PROCESO],
            fecha_creacion__lt=timezone.now() - timedelta(days=3),
        ).count()

        return Response({
            "total": total,
            "pendientes": por_estado.get(Estado.PENDIENTE, 0),
            "en_proceso": por_estado.get(Estado.EN_PROCESO, 0),
            "resueltos": por_estado.get(Estado.RESUELTO, 0),
            "cerrados": por_estado.get(Estado.CERRADO, 0),
            "criticos": qs.filter(prioridad="critica").count(),
            "tiempo_promedio_resolucion_horas": promedio_horas,
            "reportes_estancados_mas_3_dias": vencidos,
        })


class PorMesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = _queryset_base(request)
        datos = (
            qs.annotate(mes=TruncMonth("fecha_creacion"))
            .values("mes")
            .annotate(total=Count("id"))
            .order_by("mes")
        )
        return Response([{"mes": d["mes"].strftime("%Y-%m"), "total": d["total"]} for d in datos])


class PorTipoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = _queryset_base(request)
        datos = qs.values("tipo_tarea__nombre").annotate(total=Count("id")).order_by("-total")
        return Response([{"tipo": d["tipo_tarea__nombre"], "total": d["total"]} for d in datos])


class PorAreaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = _queryset_base(request)
        datos = qs.values("area__nombre").annotate(total=Count("id")).order_by("-total")[:15]
        return Response([{"area": d["area__nombre"], "total": d["total"]} for d in datos])


class PorTecnicoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = _queryset_base(request)
        datos = (
            qs.exclude(tecnico_asignado__isnull=True)
            .values("tecnico_asignado__first_name", "tecnico_asignado__last_name", "tecnico_asignado__username")
            .annotate(
                total=Count("id"),
                resueltos=Count("id", filter=Q(estado=Estado.RESUELTO)),
            )
            .order_by("-total")
        )
        resultado = []
        for d in datos:
            nombre = (
                f"{d['tecnico_asignado__first_name']} {d['tecnico_asignado__last_name']}".strip()
                or d["tecnico_asignado__username"]
            )
            resultado.append({"tecnico": nombre, "total": d["total"], "resueltos": d["resueltos"]})
        return Response(resultado)


class RankingTecnicosView(APIView):
    """
    Ranking automático de técnicos ordenado por reportes resueltos
    y tiempo promedio de resolución.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = _queryset_base(request).filter(estado__in=[Estado.RESUELTO, Estado.CERRADO])

        datos = (
            qs.exclude(tecnico_asignado__isnull=True)
            .values(
                "tecnico_asignado__id",
                "tecnico_asignado__first_name",
                "tecnico_asignado__last_name",
                "tecnico_asignado__username",
            )
            .annotate(
                reportes_resueltos=Count("id"),
                tiempo_promedio=Avg(
                    ExpressionWrapper(
                        F("fecha_resolucion") - F("fecha_creacion"),
                        output_field=DurationField(),
                    )
                ),
            )
            .order_by("-reportes_resueltos", "tiempo_promedio")[:10]
        )

        resultado = []
        for i, d in enumerate(datos):
            nombre = (
                f"{d['tecnico_asignado__first_name']} {d['tecnico_asignado__last_name']}".strip()
                or d["tecnico_asignado__username"]
            )
            tiempo_h = round(d["tiempo_promedio"].total_seconds() / 3600, 1) if d["tiempo_promedio"] else None
            resultado.append({
                "id": d["tecnico_asignado__id"],
                "nombre": nombre,
                "reportes_resueltos": d["reportes_resueltos"],
                "tiempo_promedio_horas": tiempo_h,
                "posicion": i + 1,
            })

        return Response(resultado)