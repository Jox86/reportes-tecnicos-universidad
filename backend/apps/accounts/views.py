from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import LoginSerializer, _rol_principal


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        roles = list(user.groups.values_list("name", flat=True))
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "nombre": user.get_full_name() or user.username,
                "email": user.email,
                "roles": roles,
                "is_superuser": user.is_superuser,
                "rol_principal": _rol_principal(roles, user.is_superuser),
            }
        )



# apps/accounts/views.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone

from .serializers import LoginSerializer, _rol_principal


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        roles = list(user.groups.values_list("name", flat=True))
        return Response({
            "id": user.id,
            "username": user.username,
            "nombre": user.get_full_name() or user.username,
            "email": user.email,
            "roles": roles,
            "is_superuser": user.is_superuser,
            "rol_principal": _rol_principal(roles, user.is_superuser),
        })


class EliminarCuentaView(APIView):
    """
    Permite al usuario eliminar su propia cuenta.
    - Anonimiza los reportes creados por él (los reasigna al usuario eliminado).
    - Anonimiza los datos personales del usuario.
    - Desactiva la cuenta (no la borra para no romper FKs).
    - Registra la acción.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user

        if user.is_superuser:
            return Response(
                {"error": "Un superusuario no puede eliminar su propia cuenta desde aquí."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 1. Anonimizar los reportes donde este usuario era creador
        from apps.core.models import Reporte
        Reporte.objects.filter(creado_por=user).update(
            usuario_nombre="[Usuario eliminado]",
            usuario_correo="",
            usuario_cargo="",
        )

        # 2. Anonimizar el reporte donde era técnico asignado (solo guarda el ID)
        # No hace falta porque el FK se mantiene, solo desactivamos el user

        # 3. Anonimizar datos personales del usuario
        username_original = user.username
        user.username = f"eliminado_{user.id}"
        user.first_name = "Usuario"
        user.last_name = "Eliminado"
        user.email = ""
        user.is_active = False
        user.save()

        # 4. Eliminar de los grupos
        user.groups.clear()

        # 5. Eliminar el perfil si existe
        try:
            from .models import PerfilUsuario
            PerfilUsuario.objects.filter(user=user).delete()
        except Exception:
            pass

        # 6. Log de auditoría
        import logging
        logging.getLogger(__name__).info(
            f"Cuenta eliminada: {username_original} (ID {user.id}) - {timezone.now()}"
        )

        return Response(
            {"mensaje": "Tu cuenta ha sido eliminada correctamente."},
            status=status.HTTP_200_OK,
        )