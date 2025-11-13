# users/models.py
from django.db import models

# Create your models here.
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", UserStatus.ACTIVE)
        extra_fields.setdefault("empresa", None)
        return self.create_user(email, password, **extra_fields)


# class RoleChoices(models.TextChoices):
#     ADMIN = 'ADMIN', 'Administrador'
#     SALES_AGENT = 'SALES_AGENT', 'Agente de ventas'
#     CUSTOMER = 'CUSTOMER', 'Cliente'


class Role(models.Model):
    empresa = models.ForeignKey(
        "tenants.Empresa", on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    esta_activo = models.BooleanField(default=True)
    class Meta:
        db_table = "role"

    @property
    def display_name(self):
        return self.name.capitalize()

    def __str__(self):
        return self.name


class Module(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        db_table = "module"

    def __str__(self):
        return self.name


class Permission(models.Model):
    empresa = models.ForeignKey(
        "tenants.Empresa", on_delete=models.CASCADE, null=True, blank=True
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="privileges")
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name="permissions"
    )
    can_view = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        db_table = "permission"
        unique_together = ("role", "module")

    def __str__(self):
        return f"{self.role.name} → {self.module.name}"


class UserStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Activo"
    INACTIVE = "INACTIVE", "Inactivo"


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=150, blank=True)
    apellido = models.CharField(max_length=150, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )
    empresa = models.ForeignKey(
        "tenants.Empresa",
        on_delete=models.CASCADE,
        related_name="usuarios",
        null=True,
        blank=True,
        default=1,
    )
    # django required fields
    status = models.CharField(
        max_length=20, choices=UserStatus.choices, default=UserStatus.ACTIVE
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    esta_activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "user"

    def __str__(self):
        return self.email
