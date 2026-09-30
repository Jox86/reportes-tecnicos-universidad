# apps/core/views.py
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    ArchivoReporte,
    Area,
    Estado,
    HistorialEstado,
    Reporte,
    TipoArea,
    TipoTarea,
    Ubicacion,
)
from .permissions import CatalogoPermission, ReportePermission, es_admin, es_tecnico, reportes_visibles_para
from .serializers import (
    ArchivoReporteSerializer,
    AreaSerializer,
    EquipoReporteSerializer,
    ReporteListSerializer,
    ReporteSerializer,
    TipoAreaSerializer,
    TipoTareaSerializer,
    UbicacionSerializer,
)

User = get_user_model()


# ---------------------------------------------------------------------------
# Catálogos
# ---------------------------------------------------------------------------
class TipoAreaViewSet(viewsets.ModelViewSet):
    queryset = TipoArea.objects.all()
    serializer_class = TipoAreaSerializer
    permission_classes = [IsAuthenticated, CatalogoPermission]


class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [IsAuthenticated, CatalogoPermission]


class UbicacionViewSet(viewsets.ModelViewSet):
    queryset = Ubicacion.objects.all()
    serializer_class = UbicacionSerializer
    permission_classes = [IsAuthenticated, CatalogoPermission]


class TipoTareaViewSet(viewsets.ModelViewSet):
    """Cualquier usuario autenticado puede crear tipos de tarea."""
    queryset = TipoTarea.objects.filter(activo=True)
    serializer_class = TipoTareaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)


# ---------------------------------------------------------------------------
# Reportes
# ---------------------------------------------------------------------------
class ReporteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ReportePermission]

    def get_queryset(self):
        qs = Reporte.objects.select_related(
            "area", "tipo_tarea", "tecnico_asignado", "creado_por"
        ).prefetch_related("equipos", "archivos", "historial")
        return reportes_visibles_para(self.request.user, qs)

    def get_serializer_class(self):
        if self.action == "list":
            return ReporteListSerializer
        return ReporteSerializer

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)

    def perform_update(self, serializer):
        """Registra en historial si cambia el estado."""
        instance = self.get_object()
        estado_anterior = instance.estado
        reporte = serializer.save()
        if estado_anterior != reporte.estado:
            HistorialEstado.objects.create(
                reporte=reporte,
                estado_anterior=estado_anterior,
                estado_nuevo=reporte.estado,
                usuario=self.request.user,
                comentario="Cambio desde edición",
            )
            if reporte.estado in [Estado.RESUELTO, Estado.CERRADO] and not reporte.fecha_resolucion:
                from django.utils import timezone
                reporte.fecha_resolucion = timezone.now()
                reporte.save(update_fields=["fecha_resolucion"])

    @action(detail=True, methods=["patch"], url_path="actualizar-rapido")
    def actualizar_rapido(self, request, pk=None):
        """Endpoint para edición inline desde la tabla de reportes."""
        reporte = self.get_object()
        estado_anterior = reporte.estado

        if "estado" in request.data:
            reporte.estado = request.data["estado"]
            if reporte.estado in [Estado.RESUELTO, Estado.CERRADO] and not reporte.fecha_resolucion:
                from django.utils import timezone
                reporte.fecha_resolucion = timezone.now()
            if estado_anterior != reporte.estado:
                HistorialEstado.objects.create(
                    reporte=reporte,
                    estado_anterior=estado_anterior,
                    estado_nuevo=reporte.estado,
                    usuario=request.user,
                    comentario="Cambio rápido desde listado",
                )

        if "tecnico_asignado" in request.data:
            tecnico_id = request.data["tecnico_asignado"]
            reporte.tecnico_asignado = User.objects.get(pk=tecnico_id) if tecnico_id else None

        reporte.save()
        return Response(ReporteSerializer(reporte, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="cambiar-estado")
    def cambiar_estado(self, request, pk=None):
        """Cambio de estado con comentario y solución."""
        reporte = self.get_object()
        nuevo_estado = request.data.get("estado")
        comentario = request.data.get("comentario", "")
        solucion = request.data.get("solucion", "")

        # Validar que el estado sea válido
        estados_validos = [e[0] for e in Estado.choices]
        if nuevo_estado not in estados_validos:
            return Response(
                {"error": f"Estado inválido: {nuevo_estado}. Válidos: {estados_validos}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        estado_anterior = reporte.estado
        reporte.estado = nuevo_estado
        if solucion:
            reporte.solucion = solucion
        if nuevo_estado in [Estado.RESUELTO, Estado.CERRADO] and not reporte.fecha_resolucion:
            from django.utils import timezone
            reporte.fecha_resolucion = timezone.now()
        reporte.save()

        HistorialEstado.objects.create(
            reporte=reporte,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            comentario=comentario,
            usuario=request.user,
        )

        # Notificar por correo (opcional, no debe romper el flujo)
        if reporte.usuario_correo and nuevo_estado in [Estado.RESUELTO, Estado.CERRADO]:
            try:
                from .notificaciones import notificar_resolucion
                notificar_resolucion(reporte)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error al enviar notificación para {reporte.codigo}: {e}")

        return Response(ReporteSerializer(reporte, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="subir-archivo")
    def subir_archivo(self, request, pk=None):
        reporte = self.get_object()
        archivo = request.FILES.get("archivo")
        if not archivo:
            return Response({"error": "No se envió archivo"}, status=status.HTTP_400_BAD_REQUEST)
        obj = ArchivoReporte.objects.create(
            reporte=reporte,
            archivo=archivo,
            nombre=archivo.name,
            subido_por=request.user,
        )
        return Response(ArchivoReporteSerializer(obj, context={"request": request}).data)

@action(detail=True, methods=["delete"], url_path=r"eliminar-archivo/(?P<archivo_id>\d+)")
def eliminar_archivo(self, request, pk=None, archivo_id=None):
    """Elimina un archivo adjunto de un reporte."""
    reporte = self.get_object()
    try:
        archivo = reporte.archivos.get(id=archivo_id)
        # Verificar permisos
        es_admin = request.user.is_superuser or request.user.groups.filter(name="Administrador").exists()
        if not es_admin and archivo.subido_por_id != request.user.id:
            return Response(
                {"error": "No tienes permiso para eliminar este archivo."},
                status=status.HTTP_403_FORBIDDEN,
            )
        archivo.archivo.delete(save=False)
        archivo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ArchivoReporte.DoesNotExist:
        return Response(
            {"error": "Archivo no encontrado."},
            status=status.HTTP_404_NOT_FOUND,
        )
    
# ---------------------------------------------------------------------------
# Búsqueda LDAP
# ---------------------------------------------------------------------------
class BuscarUsuarioLDAPView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query or len(query) < 2:
            return Response([])

        resultados = []
        usuarios = User.objects.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
        )[:10]

        for u in usuarios:
            resultados.append({
                "id": u.id,
                "username": u.username,
                "nombre_completo": u.get_full_name() or u.username,
                "email": u.email,
                "cargo": getattr(u, "cargo", "") or "",
            })

        return Response(resultados)


# ---------------------------------------------------------------------------
# Técnicos
# ---------------------------------------------------------------------------
class TecnicosViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from django.conf import settings
        return User.objects.filter(
            groups__name__in=[settings.ROL_ADMIN, settings.ROL_TECNICO]
        ).distinct().order_by("first_name", "last_name")

    def list(self, request, *args, **kwargs):
        data = [
            {
                "id": u.id,
                "username": u.username,
                "nombre_completo": u.get_full_name() or u.username,
                "email": u.email,
            }
            for u in self.get_queryset()
        ]
        return Response(data)