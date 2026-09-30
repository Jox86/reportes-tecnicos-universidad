# apps/accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User

from .models import PerfilUsuario


class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = "Perfil extendido"
    fk_name = "user"


class UserAdmin(BaseUserAdmin):
    inlines = [PerfilUsuarioInline]
    list_display = ("username", "get_full_name", "email", "get_rol", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "is_superuser", "groups")
    search_fields = ("username", "first_name", "last_name", "email")

    def get_rol(self, obj):
        try:
            return obj.perfil.rol_principal
        except PerfilUsuario.DoesNotExist:
            return "Sin perfil"
    get_rol.short_description = "Rol"

    def get_full_name(self, obj):
        return obj.get_full_name() or "—"
    get_full_name.short_description = "Nombre completo"


# Re-registrar User con el admin extendido
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("user", "nombre_completo", "cargo", "area", "activo_en_sistema")
    list_filter = ("activo_en_sistema", "area")
    search_fields = ("user__username", "user__first_name", "user__last_name", "cargo")