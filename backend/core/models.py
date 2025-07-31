from django.db import models

from django.contrib.auth.models import User

class BaseEntity(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Priority(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    CRITICAL = 'critical', 'Critical'

class TicketStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    IN_PROGRESS = 'in_progress', 'In Progress'
    RESOLVED = 'resolved', 'Resolved'
    CANCELED = 'canceled', 'Canceled'

class Ticket(BaseEntity):
    title = models.CharField(max_length=255)
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    status = models.CharField(
        max_length=20,
        choices=TicketStatus.choices,
        default=TicketStatus.OPEN
    )
    description = models.TextField(blank=True, null=True, default=None)
    attendant = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Chamado"
        verbose_name_plural = "Chamados"
