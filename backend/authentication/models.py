from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


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


@receiver(post_save, sender=User)
def add_attendant_permissions(sender, instance, created, **kwargs):
    if instance.profile == 'attendant':
        try:
            from core.models import Ticket
            content_type = ContentType.objects.get_for_model(Ticket)
            add_permission = Permission.objects.get(content_type=content_type, codename='add_ticket')
            change_permission = Permission.objects.get(content_type=content_type, codename='change_ticket')
            view_permission = Permission.objects.get(content_type=content_type, codename='view_ticket')

            if not instance.user_permissions.filter(codename='add_ticket').exists():
                instance.user_permissions.add(add_permission, change_permission, view_permission)

            if not instance.is_staff:
                instance.is_staff = True
                instance.save(update_fields=['is_staff'])

        except Exception as e:
            print(f"Erro ao adicionar permissões para atendente: {e}")
