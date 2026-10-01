# apps/core/views.py
import logging

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
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
from .permissions import (
    CatalogoPermission,
    ReportePermission,
    es_admin,
    es_tecnico,
    reportes_visibles_para,
)
from .serializers import (
    ArchivoReporteSerializer,
    AreaSerializer,
    ReporteListSerializer,
    ReporteSerializer,
    TipoAreaSerializer,
    TipoTareaSerializer,
    UbicacionSerializer,
)

logger = logging.getLogger(__name__)
User = get_user_model()


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
    queryset = TipoTarea.objects.filter(activo=True)
    serializer_class = TipoTareaSerializer
    permission_classes = [IsAuthenticated, CatalogoPermission]

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)


class ReporteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ReportePermission]

    def get_queryset(self):
        qs = Reporte.objects.select_related(
            "area", "tipo_tarea", "tecnico_asignado", "creado_por"
        ).prefetch_related("equipos", "archivos", "historial")
        return reportes_visibles_para(self.request.user, qs)

    def get_serializer_class(self):
        return ReporteListSerializer if self.action == "list" else ReporteSerializer

    def perform_create(self, serializer):
        reporte = serializer.save(creado_por=self.request.user)
        try:
            from .notificaciones import notificar_nuevo_reporte
            notificar_nuevo_reporte(reporte)
        except Exception:
            logger.exception("Error notificando nuevo reporte")

    def perform_update(self, serializer):
        instance = self.get_object()
        estado_anterior = instance.estado
        tecnico_anterior = instance.tecnico_asignado_id
        reporte = serializer.save()

        if estado_anterior != reporte.estado:
            HistorialEstado.objects.create(
                reporte=reporte,
                estado_anterior=estado_anterior,
                estado_nuevo=reporte.estado,
                usuario=self.request.user,
                comentario="Cambio desde edición",
            )
            if reporte.estado in (Estado.RESUELTO, Estado.CERRADO) and not reporte.fecha_resolucion:
                reporte.fecha_resolucion = timezone.now()
                reporte.save(update_fields=["fecha_resolucion"])
            try:
                from .notificaciones import notificar_resolucion
                notificar_resolucion(reporte, estado_anterior)
            except Exception:
                logger.exception("Error notificando cambio de estado")

        if reporte.tecnico_asignado_id and reporte.tecnico_asignado_id != tecnico_anterior:
            try:
                from .notificaciones import notificar_asignacion
                notificar_asignacion(reporte)
            except Exception:
                logger.exception("Error notificando asignación")

    @action(detail=True, methods=["patch"], url_path="actualizar-rapido")
    def actualizar_rapido(self, request, pk=None):
        reporte = self.get_object()
        estado_anterior = reporte.estado

        if "estado" in request.data:
            nuevo_estado = request.data["estado"]
            if nuevo_estado not in [value for value, _ in Estado.choices]:
                return Response({"error": "Estado inválido."}, status=status.HTTP_400_BAD_REQUEST)
            reporte.estado = nuevo_estado
            if nuevo_estado in (Estado.RESUELTO, Estado.CERRADO) and not reporte.fecha_resolucion:
                reporte.fecha_resolucion = timezone.now()
            if estado_anterior != nuevo_estado:
                HistorialEstado.objects.create(
                    reporte=reporte,
                    estado_anterior=estado_anterior,
                    estado_nuevo=nuevo_estado,
                    usuario=request.user,
                    comentario="Cambio rápido desde listado",
                )

        if "tecnico_asignado" in request.data:
            tecnico_id = request.data["tecnico_asignado"]
            if tecnico_id:
                try:
                    reporte.tecnico_asignado = User.objects.get(
                        pk=tecnico_id,
                        is_active=True,
                        groups__name__in=["Tecnico", "Administrador"],
                    )
                except User.DoesNotExist:
                    return Response(
                        {"error": "Técnico no válido."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                reporte.tecnico_asignado = None

        reporte.save()
        return Response(ReporteSerializer(reporte, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="cambiar-estado")
    def cambiar_estado(self, request, pk=None):
        reporte = self.get_object()
        nuevo_estado = request.data.get("estado")
        comentario = str(request.data.get("comentario", ""))[:2000]
        solucion = request.data.get("solucion")

        if nuevo_estado not in [value for value, _ in Estado.choices]:
            return Response({"error": "Estado inválido."}, status=status.HTTP_400_BAD_REQUEST)

        estado_anterior = reporte.estado
        reporte.estado = nuevo_estado
        if solucion is not None:
            reporte.solucion = str(solucion)[:10000]
        if nuevo_estado in (Estado.RESUELTO, Estado.CERRADO) and not reporte.fecha_resolucion:
            reporte.fecha_resolucion = timezone.now()
        reporte.save()

        HistorialEstado.objects.create(
            reporte=reporte,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            comentario=comentario,
            usuario=request.user,
        )

        if nuevo_estado != estado_anterior:
            try:
                from .notificaciones import notificar_resolucion
                notificar_resolucion(reporte, estado_anterior)
            except Exception:
                logger.exception("Error notificando cambio de estado")

        return Response(ReporteSerializer(reporte, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="subir-archivo")
    def subir_archivo(self, request, pk=None):
        reporte = self.get_object()
        archivo = request.FILES.get("archivo")
        if not archivo:
            return Response({"error": "No se envió archivo."}, status=status.HTTP_400_BAD_REQUEST)

        max_size = 10 * 1024 * 1024
        allowed_types = {
            "application/pdf",
            "image/jpeg",
            "image/png",
            "text/plain",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }
        if archivo.size > max_size:
            return Response({"error": "El archivo supera el límite de 10 MB."}, status=status.HTTP_400_BAD_REQUEST)
        if archivo.content_type not in allowed_types:
            return Response({"error": "Tipo de archivo no permitido."}, status=status.HTTP_400_BAD_REQUEST)

        obj = ArchivoReporte.objects.create(
            reporte=reporte,
            archivo=archivo,
            nombre=archivo.name[:255],
            subido_por=request.user,
        )
        return Response(
            ArchivoReporteSerializer(obj, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["delete"], url_path=r"eliminar-archivo/(?P<archivo_id>\d+)")
    def eliminar_archivo(self, request, pk=None, archivo_id=None):
        reporte = self.get_object()
        try:
            archivo = reporte.archivos.get(id=archivo_id)
        except ArchivoReporte.DoesNotExist:
            return Response({"error": "Archivo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if not es_admin(request.user) and archivo.subido_por_id != request.user.id:
            return Response(
                {"error": "No tienes permiso para eliminar este archivo."},
                status=status.HTTP_403_FORBIDDEN,
            )

        archivo.archivo.delete(save=False)
        archivo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BuscarUsuarioLDAPView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query or len(query) < 2:
            return Response([])

        usuarios = User.objects.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query),
            is_active=True,
        ).order_by("username")[:10]

        return Response([
            {
                "id": u.id,
                "username": u.username,
                "nombre_completo": u.get_full_name() or u.username,
                "email": u.email,
            }
            for u in usuarios
        ])


class TecnicosViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from django.conf import settings
        return User.objects.filter(
            groups__name__in=[settings.ROL_ADMIN, settings.ROL_TECNICO],
            is_active=True,
        ).distinct().order_by("first_name", "last_name")

    def list(self, request, *args, **kwargs):
        return Response([
            {
                "id": u.id,
                "username": u.username,
                "nombre_completo": u.get_full_name() or u.username,
                "email": u.email,
            }
            for u in self.get_queryset()
        ])


from .notificaciones_models import Notificacion
from .serializers import NotificacionSerializer


class NotificacionesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notificacion.objects.filter(usuario=self.request.user)

    @action(detail=False, methods=["post"], url_path="marcar-leidas")
    def marcar_leidas(self, request):
        actualizadas = self.get_queryset().filter(leida=False).update(leida=True)
        return Response({"actualizadas": actualizadas})

    @action(detail=True, methods=["post"], url_path="marcar-leida")
    def marcar_leida(self, request, pk=None):
        notif = self.get_object()
        notif.leida = True
        notif.save(update_fields=["leida"])
        return Response({"ok": True})

    @action(detail=False, methods=["get"], url_path="pendientes")
    def pendientes(self, request):
        qs = self.get_queryset().filter(leida=False)[:10]
        return Response({
            "total": self.get_queryset().filter(leida=False).count(),
            "no_leidas": NotificacionSerializer(qs, many=True).data,
        })
