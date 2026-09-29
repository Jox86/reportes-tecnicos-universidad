# apps/exports/urls.py
from django.urls import path

from .views import (
    ExportarReporteExcel,
    ExportarReportePDF,
    ExportarReporteWord,
    ExportarReportesExcel,
)

urlpatterns = [
    path("reportes/excel/", ExportarReportesExcel.as_view()),
    path("reportes/<int:pk>/pdf/", ExportarReportePDF.as_view()),
    path("reportes/<int:pk>/excel/", ExportarReporteExcel.as_view()),
    path("reportes/<int:pk>/word/", ExportarReporteWord.as_view()),
]