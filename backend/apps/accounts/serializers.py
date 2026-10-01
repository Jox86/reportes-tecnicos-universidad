# apps/accounts/serializers.py
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.conf import settings

def _rol_principal(roles, is_superuser):
    """Devuelve el rol de mayor jerarquía del usuario."""
    if is_superuser or settings.ROL_ADMIN in roles:
        return settings.ROL_ADMIN
    if settings.ROL_AUDITOR in roles:
        return settings.ROL_AUDITOR
    if settings.ROL_TECNICO in roles:
        return settings.ROL_TECNICO
    return None


class LoginSerializer(TokenObtainPairSerializer):
    """
    Serializer de login que funciona tanto para LDAP como para usuarios locales.
    El backend de autenticación (LDAPBackend + ModelBackend) se encarga de validar.
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # Sincronizar roles desde LDAP (si aplica)
        self._sincronizar_roles(user)

        roles = list(user.groups.values_list("name", flat=True))
        data["usuario"] = {
            "id": user.id,
            "username": user.username,
            "nombre": user.get_full_name() or user.username,
            "email": user.email,
            "roles": roles,
            "is_superuser": user.is_superuser,
            "rol_principal": _rol_principal(roles, user.is_superuser),
        }
        return data

    def _sincronizar_roles(self, user):
        """Aplica el mapeo AD_ROLE_GROUP_MAPPING después de autenticar."""
        from django.conf import settings

        mapping = getattr(settings, "AD_ROLE_GROUP_MAPPING", {})
        if not mapping or user.is_superuser:
            return

        # Grupos LDAP del usuario (los nombres vienen del AD)
        ldap_groups = set(user.groups.values_list("name", flat=True))
        roles_detectados = set()

        for ad_group, rol_interno in mapping.items():
            if ad_group in ldap_groups:
                roles_detectados.add(rol_interno)

        # Si no se detectó ningún rol, asignar el rol por defecto
        if not roles_detectados:
            roles_detectados.add(settings.ROL_POR_DEFECTO)

        # Asignar grupos internos al usuario
        for rol in roles_detectados:
            grupo, _ = Group.objects.get_or_create(name=rol)
            user.groups.add(grupo)