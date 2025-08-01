from django.db import models

from authentication.models import User


class BaseEntity(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Priority(models.TextChoices):
    LOW = 'low', 'Baixa'
    MEDIUM = 'medium', 'Média'
    HIGH = 'high', 'Alta'
    CRITICAL = 'critical', 'Crítica'


class TicketStatus(models.TextChoices):
    OPEN = 'open', 'Aberto'
    IN_PROGRESS = 'in_progress', 'Em Atendimento'
    RESOLVED = 'resolved', 'Resolvido'
    CANCELED = 'canceled', 'Cancelado'


class Ticket(BaseEntity):
    title = models.CharField(verbose_name='Título', max_length=255)
    priority = models.CharField(
        verbose_name='Prioridade',
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    status = models.CharField(
        verbose_name='Status',
        max_length=20,
        choices=TicketStatus.choices,
        default=TicketStatus.OPEN
    )
    description = models.TextField(verbose_name='Descrição', blank=True, null=True, default=None)
    attendant = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Atendente')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Chamado"
        verbose_name_plural = "Chamados"
