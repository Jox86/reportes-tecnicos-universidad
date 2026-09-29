# apps/exports/views.py
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.core.filters import ReporteFilter
from apps.core.models import Reporte
from apps.core.permissions import reportes_visibles_para

from .excel import generar_excel_reportes, generar_excel_reporte_individual
from .pdf import generar_pdf_reporte, generar_pdf_reporte_individual
from .word import generar_word_reporte


def _queryset_permitido(request):
    qs = Reporte.objects.select_related(
        "area", "tipo_tarea", "tecnico_asignado", "creado_por"
    ).prefetch_related("equipos", "archivos", "historial")
    return reportes_visibles_para(request.user, qs)


class ExportarReportePDF(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        reporte = get_object_or_404(_queryset_permitido(request), pk=pk)
        buffer = generar_pdf_reporte_individual(reporte)
        response = HttpResponse(buffer.read(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{reporte.codigo}.pdf"'
        return response


class ExportarReporteExcel(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        reporte = get_object_or_404(_queryset_permitido(request), pk=pk)
        buffer = generar_excel_reporte_individual(reporte)
        response = HttpResponse(
            buffer.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{reporte.codigo}.xlsx"'
        return response


class ExportarReporteWord(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        reporte = get_object_or_404(_queryset_permitido(request), pk=pk)
        buffer = generar_word_reporte(reporte)
        response = HttpResponse(
            buffer.read(),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        response["Content-Disposition"] = f'attachment; filename="{reporte.codigo}.docx"'
        return response


class ExportarReportesExcel(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = _queryset_permitido(request)
        qs = ReporteFilter(request.GET, queryset=qs).qs
        buffer = generar_excel_reportes(qs)
        response = HttpResponse(
            buffer.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="reportes.xlsx"'
        return response