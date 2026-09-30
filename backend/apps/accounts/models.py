# apps/accounts/models.py
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class PerfilUsuario(models.Model):
    """
    Extiende al User de Django con campos adicionales:
    - cargo: cargo o dependencia del usuario
    - telefono: teléfono de contacto
    - area: área a la que pertenece
    - activo_en_sistema: si puede o no acceder
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    cargo = models.CharField("Cargo / dependencia", max_length=150, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    area = models.ForeignKey(
        "core.Area",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios",
    )
    activo_en_sistema = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuarios"

    def __str__(self):
        return f"Perfil de {self.user.username}"

    @property
    def nombre_completo(self):
        return self.user.get_full_name() or self.user.username

    @property
    def rol_principal(self):
        """Devuelve el rol de mayor jerarquía del usuario."""
        roles = list(self.user.groups.values_list("name", flat=True))
        if self.user.is_superuser or "Administrador" in roles:
            return "Administrador"
        if "Auditor" in roles:
            return "Auditor"
        if "Tecnico" in roles:
            return "Tecnico"
        return "Sin rol"


# ---------------------------------------------------------------------------
# Señal: crear PerfilUsuario automáticamente al crear un User
# ---------------------------------------------------------------------------
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.get_or_create(user=instance)