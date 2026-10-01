from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import Estado, Reporte
from apps.core.permissions import es_admin, es_auditor, es_director, reportes_visibles_para

User = get_user_model()


class EstadisticasPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (es_admin(user) or es_auditor(user) or es_director(user))
        )


def _queryset_base(request):
    qs = reportes_visibles_para(request.user, Reporte.objects.all())
    desde = request.GET.get("desde")
    hasta = request.GET.get("hasta")
    if desde:
        qs = qs.filter(fecha_creacion__date__gte=desde)
    if hasta:
        qs = qs.filter(fecha_creacion__date__lte=hasta)
    return qs


class ResumenView(APIView):
    permission_classes = [EstadisticasPermission]

    def get(self, request):
        qs = _queryset_base(request)
        por_estado = {row["estado"]: row["total"] for row in qs.values("estado").annotate(total=Count("id"))}
        total = qs.count()
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
    permission_classes = [EstadisticasPermission]

    def get(self, request):
        datos = _queryset_base(request).annotate(mes=TruncMonth("fecha_creacion")).values("mes").annotate(total=Count("id")).order_by("mes")
        return Response([{"mes": d["mes"].strftime("%Y-%m"), "total": d["total"]} for d in datos])


class PorTipoView(APIView):
    permission_classes = [EstadisticasPermission]

    def get(self, request):
        datos = _queryset_base(request).values("tipo_tarea__nombre").annotate(total=Count("id")).order_by("-total")
        return Response([{"tipo": d["tipo_tarea__nombre"], "total": d["total"]} for d in datos])


class PorAreaView(APIView):
    permission_classes = [EstadisticasPermission]

    def get(self, request):
        datos = _queryset_base(request).values("area__nombre").annotate(total=Count("id")).order_by("-total")[:15]
        return Response([{"area": d["area__nombre"], "total": d["total"]} for d in datos])


class PorTecnicoView(APIView):
    permission_classes = [EstadisticasPermission]

    def get(self, request):
        datos = (
            _queryset_base(request)
            .exclude(tecnico_asignado__isnull=True)
            .values("tecnico_asignado__first_name", "tecnico_asignado__last_name", "tecnico_asignado__username")
            .annotate(total=Count("id"), resueltos=Count("id", filter=Q(estado__in=[Estado.RESUELTO, Estado.CERRADO])))
            .order_by("-total")
        )
        resultado = []
        for d in datos:
            nombre = f"{d['tecnico_asignado__first_name']} {d['tecnico_asignado__last_name']}".strip() or d["tecnico_asignado__username"]
            resultado.append({"tecnico": nombre, "total": d["total"], "resueltos": d["resueltos"]})
        return Response(resultado)


class RankingTecnicosView(APIView):
    permission_classes = [EstadisticasPermission]

    def get(self, request):
        tecnicos = User.objects.filter(
            groups__name__in=["Tecnico", "Administrador"],
            is_active=True,
        ).distinct()
        resultado = []
        for tecnico in tecnicos:
            resueltos_qs = Reporte.objects.filter(
                tecnico_asignado=tecnico,
                estado__in=[Estado.RESUELTO, Estado.CERRADO],
            )
            reportes_resueltos = resueltos_qs.count()
            tiempo_promedio = resueltos_qs.filter(fecha_resolucion__isnull=False).annotate(
                duracion=ExpressionWrapper(F("fecha_resolucion") - F("fecha_creacion"), output_field=DurationField())
            ).aggregate(promedio=Avg("duracion"))["promedio"]
            tiempo_horas = round(tiempo_promedio.total_seconds() / 3600, 1) if tiempo_promedio else None
            resultado.append({
                "id": tecnico.id,
                "nombre": tecnico.get_full_name() or tecnico.username,
                "username": tecnico.username,
                "reportes_resueltos": reportes_resueltos,
                "tiempo_promedio_horas": tiempo_horas,
                "es_admin": es_admin(tecnico),
            })

        resultado.sort(key=lambda t: (
            -t["reportes_resueltos"],
            t["tiempo_promedio_horas"] if t["tiempo_promedio_horas"] is not None else float("inf"),
        ))
        for i, t in enumerate(resultado, 1):
            t["posicion"] = i
        return Response(resultado)
