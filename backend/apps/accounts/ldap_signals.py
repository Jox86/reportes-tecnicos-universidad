"""
Cuando un usuario inicia sesión vía LDAP/Active Directory, django-auth-ldap
"espeja" sus grupos del AD tal cual (mismo nombre de CN). Como el nombre del
grupo en el AD normalmente no coincide con nuestros 4 roles internos
(Administrador/Auditor/Director/Tecnico), esta señal hace la traducción
usando settings.AD_ROLE_GROUP_MAPPING.

Si el proyecto no tiene LDAP configurado (AUTH_LDAP_SERVER_URI vacío), este
archivo simplemente no hace nada porque la señal de django_auth_ldap no
existe / nunca se dispara.
"""
from django.conf import settings

try:
    from django_auth_ldap.backend import populate_user
except ImportError:  # django-auth-ldap no instalado todavía
    populate_user = None


def _asignar_rol_desde_ldap(sender, user, ldap_user, **kwargs):
    from django.contrib.auth.models import Group

    mapping = getattr(settings, "AD_ROLE_GROUP_MAPPING", {})
    if not mapping:
        return

    grupos_ad = set(ldap_user.group_names or [])
    roles_asignados = {rol for grupo_ad, rol in mapping.items() if grupo_ad in grupos_ad}

    # Limpia roles anteriores gestionados por este mapeo y aplica los vigentes
    user.groups.remove(*Group.objects.filter(name__in=settings.ROLES_DISPONIBLES))
    if roles_asignados:
        grupos = Group.objects.filter(name__in=roles_asignados)
        user.groups.add(*grupos)


if populate_user is not None:
    populate_user.connect(_asignar_rol_desde_ldap)
