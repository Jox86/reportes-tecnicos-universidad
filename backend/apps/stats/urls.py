# apps/stats/urls.py
from django.urls import path

from .views import (
    PorAreaView,
    PorMesView,
    PorTecnicoView,
    PorTipoView,
    RankingTecnicosView,
    ResumenView,
)

urlpatterns = [
    path("resumen/", ResumenView.as_view()),
    path("por-mes/", PorMesView.as_view()),
    path("por-tipo/", PorTipoView.as_view()),
    path("por-area/", PorAreaView.as_view()),
    path("por-tecnico/", PorTecnicoView.as_view()),
    path("ranking/", RankingTecnicosView.as_view()),
]