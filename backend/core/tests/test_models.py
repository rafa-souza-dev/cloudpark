from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import Ticket, TicketStatus, Priority, BaseEntity
from authentication.models import UserProfile

User = get_user_model()


class BaseEntityTest(TestCase):
    def test_base_entity_abstract(self):
        self.assertTrue(BaseEntity._meta.abstract)
    
    def test_base_entity_fields(self):
        fields = [field.name for field in BaseEntity._meta.fields]
        self.assertIn('created_at', fields)
        self.assertIn('updated_at', fields)


class TicketModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            profile=UserProfile.ATTENDANT
        )
    
    def test_ticket_creation(self):
        ticket = Ticket.objects.create(
            title='Ticket de Teste',
            description='Descrição do ticket',
            priority=Priority.MEDIUM,
            status=TicketStatus.OPEN,
            attendant=self.user
        )
        
        self.assertEqual(ticket.title, 'Ticket de Teste')
        self.assertEqual(ticket.priority, Priority.MEDIUM)
        self.assertEqual(ticket.status, TicketStatus.OPEN)
        self.assertEqual(ticket.attendant, self.user)
        self.assertIsNotNone(ticket.created_at)
    
    def test_ticket_str_representation(self):
        ticket = Ticket.objects.create(
            title='Ticket de Teste',
            attendant=self.user
        )
        
        self.assertEqual(str(ticket), 'Ticket de Teste')
    
    def test_ticket_meta_verbose_names(self):
        self.assertEqual(Ticket._meta.verbose_name, 'Chamado')
        self.assertEqual(Ticket._meta.verbose_name_plural, 'Chamados')
    
    def test_ticket_default_values(self):
        ticket = Ticket.objects.create(
            title='Ticket sem valores explícitos',
            attendant=self.user
        )
        
        self.assertEqual(ticket.priority, Priority.MEDIUM)
        self.assertEqual(ticket.status, TicketStatus.OPEN)


class TicketStatusChoicesTest(TestCase):
    def test_ticket_status_choices(self):
        expected_choices = [
            ('open', 'Aberto'),
            ('in_progress', 'Em Atendimento'),
            ('resolved', 'Resolvido'),
            ('canceled', 'Cancelado')
        ]
        
        self.assertEqual(TicketStatus.choices, expected_choices)
    
    def test_ticket_status_values(self):
        self.assertEqual(TicketStatus.OPEN, 'open')
        self.assertEqual(TicketStatus.RESOLVED, 'resolved')


class PriorityChoicesTest(TestCase):
    def test_priority_choices(self):
        expected_choices = [
            ('low', 'Baixa'),
            ('medium', 'Média'),
            ('high', 'Alta'),
            ('critical', 'Crítica')
        ]
        
        self.assertEqual(Priority.choices, expected_choices)
    
    def test_priority_values(self):
        self.assertEqual(Priority.LOW, 'low')
        self.assertEqual(Priority.HIGH, 'high')


class TicketValidationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            profile=UserProfile.ATTENDANT
        )
    
    def test_ticket_title_max_length(self):
        long_title = 'A' * 255
        ticket = Ticket.objects.create(
            title=long_title,
            attendant=self.user
        )
        
        self.assertEqual(ticket.title, long_title)
    
    def test_ticket_attendant_required(self):
        with self.assertRaises(Exception):
            Ticket.objects.create(
                title='Ticket sem attendant'
            )


class TicketTimestampsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            profile=UserProfile.ATTENDANT
        )
    
    def test_ticket_created_at_auto_now_add(self):
        before_creation = timezone.now()
        ticket = Ticket.objects.create(
            title='Ticket para testar timestamps',
            attendant=self.user
        )
        after_creation = timezone.now()
        
        self.assertIsNotNone(ticket.created_at)
        self.assertGreaterEqual(ticket.created_at, before_creation)
        self.assertLessEqual(ticket.created_at, after_creation)
    
    def test_ticket_updated_at_auto_now(self):
        ticket = Ticket.objects.create(
            title='Ticket para testar updated_at',
            attendant=self.user
        )
        
        original_updated_at = ticket.updated_at
        
        import time
        time.sleep(0.1)
        
        ticket.title = 'Título atualizado'
        ticket.save()
        
        self.assertGreater(ticket.updated_at, original_updated_at) 