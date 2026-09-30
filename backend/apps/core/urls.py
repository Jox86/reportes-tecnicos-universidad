# apps/core/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import NotificacionesViewSet

from .views import (
    AreaViewSet,
    BuscarUsuarioLDAPView,
    ReporteViewSet,
    TecnicosViewSet,
    TipoAreaViewSet,
    TipoTareaViewSet,
    UbicacionViewSet,
)

router = DefaultRouter()
router.register("reportes", ReporteViewSet, basename="reporte")
router.register("areas", AreaViewSet, basename="area")
router.register("tipos-area", TipoAreaViewSet, basename="tipo-area")
router.register("ubicaciones", UbicacionViewSet, basename="ubicacion")
router.register("tipos-tarea", TipoTareaViewSet, basename="tipo-tarea")
router.register("tecnicos", TecnicosViewSet, basename="tecnico")
router.register("notificaciones", NotificacionesViewSet, basename="notificacion")

urlpatterns = [
    path("", include(router.urls)),
    path("ldap/buscar/", BuscarUsuarioLDAPView.as_view()),
]