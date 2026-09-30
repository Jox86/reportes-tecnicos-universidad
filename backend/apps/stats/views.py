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


# apps/stats/views.py
from django.contrib.auth.models import User
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Q
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import Estado, Reporte


class RankingTecnicosView(APIView):
    """
    Ranking de técnicos.
    - Incluye TODOS los usuarios con rol Técnico o Administrador.
    - Ordena por:
      1) Reportes resueltos (descendente)
      2) Tiempo promedio de resolución (ascendente)
      3) Último inicio de sesión (más reciente primero)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 1. Obtener TODOS los técnicos y admins
        tecnicos = User.objects.filter(
            groups__name__in=["Tecnico", "Administrador"],
            is_active=True,
        ).distinct()

        # 2. Calcular reportes resueltos por cada técnico
        resultado = []
        for tecnico in tecnicos:
            resueltos_qs = Reporte.objects.filter(
                tecnico_asignado=tecnico,
                estado__in=[Estado.RESUELTO, Estado.CERRADO],
            )
            reportes_resueltos = resueltos_qs.count()

            # Tiempo promedio de resolución
            tiempo_promedio = resueltos_qs.filter(
                fecha_resolucion__isnull=False
            ).annotate(
                duracion=ExpressionWrapper(
                    F("fecha_resolucion") - F("fecha_creacion"),
                    output_field=DurationField(),
                )
            ).aggregate(promedio=Avg("duracion"))["promedio"]

            tiempo_horas = (
                round(tiempo_promedio.total_seconds() / 3600, 1)
                if tiempo_promedio else None
            )

            resultado.append({
                "id": tecnico.id,
                "nombre": tecnico.get_full_name() or tecnico.username,
                "username": tecnico.username,
                "email": tecnico.email,
                "reportes_resueltos": reportes_resueltos,
                "tiempo_promedio_horas": tiempo_horas,
                "ultimo_login": tecnico.last_login.isoformat() if tecnico.last_login else None,
                "es_admin": tecnico.is_superuser or tecnico.groups.filter(name="Administrador").exists(),
            })

        # 3. Ordenar:
        #   - Primero por reportes_resueltos (desc)
        #   - Luego por tiempo_promedio (asc, los None al final)
        #   - Finalmente por last_login (desc, los más recientes primero)
        def ordenar(t):
            return (
                -t["reportes_resueltos"],
                t["tiempo_promedio_horas"] if t["tiempo_promedio_horas"] is not None else float("inf"),
                # Para last_login: los que tienen fecha van primero (orden desc)
                # y los que no tienen van al final
                -(
                    timezone.datetime.fromisoformat(t["ultimo_login"]).timestamp()
                    if t["ultimo_login"] else 0
                ),
            )

        resultado.sort(key=ordenar)

        # 4. Asignar posición
        for i, t in enumerate(resultado):
            t["posicion"] = i + 1
            # Calcular estrellas (0-5)
            r = t["reportes_resueltos"]
            if r >= 20:
                t["estrellas"] = 5
            elif r >= 15:
                t["estrellas"] = 4
            elif r >= 10:
                t["estrellas"] = 3
            elif r >= 5:
                t["estrellas"] = 2
            elif r >= 1:
                t["estrellas"] = 1
            else:
                t["estrellas"] = 0

        return Response(resultado)