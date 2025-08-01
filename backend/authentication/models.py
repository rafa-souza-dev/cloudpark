from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class UserProfile(models.TextChoices):
    ATTENDANT = 'attendant', 'Atendente'
    TECHNICIAN = 'technician', 'Técnico'


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='E-mail' ,unique=True)
    is_active = models.BooleanField(verbose_name='É ativo' ,default=True)
    is_staff = models.BooleanField(verbose_name='É membro' ,default=False)
    profile = models.CharField(
        verbose_name='Tipo de usuário',
        max_length=20,
        choices=UserProfile.choices,
        default=UserProfile.ATTENDANT
    )
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
