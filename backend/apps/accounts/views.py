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
