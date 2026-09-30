# apps/core/permissions.py
from django.conf import settings
from django.db.models import Q
from rest_framework import permissions


def roles_de(user):
    if not user or not user.is_authenticated:
        return set()
    return set(user.groups.values_list("name", flat=True))


def es_admin(user):
    return bool(user and (user.is_superuser or settings.ROL_ADMIN in roles_de(user)))


def es_auditor(user):
    return settings.ROL_AUDITOR in roles_de(user)


def es_tecnico(user):
    return settings.ROL_TECNICO in roles_de(user)


def solo_lectura(user):
    """Auditor solo consulta y exporta, no crea ni edita reportes."""
    return es_auditor(user) and not es_admin(user)


class EsAdministrador(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and es_admin(request.user))


class CatalogoPermission(permissions.BasePermission):
    """Áreas, tipos de área y ubicaciones: cualquier rol autenticado lee; solo Admin escribe."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return es_admin(request.user)


class ReportePermission(permissions.BasePermission):
    """
    - Administrador: acceso total.
    - Auditor: solo lectura (incluye exportación) sobre todos los reportes.
    - Técnico: puede crear reportes y editar/actualizar solo los suyos
      (creados por él o asignados a él).
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if es_admin(user):
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        if solo_lectura(user):
            return False
        # POST (crear) y demás métodos de escritura: solo técnicos
        return es_tecnico(user)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if es_admin(user):
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        if es_tecnico(user):
            return obj.creado_por_id == user.id or obj.tecnico_asignado_id == user.id
        return False


def reportes_visibles_para(user, queryset):
    if es_admin(user) or solo_lectura(user):
        return queryset
    if es_tecnico(user):
        return queryset.filter(Q(creado_por_id=user.id) | Q(tecnico_asignado_id=user.id))
    return queryset.none()