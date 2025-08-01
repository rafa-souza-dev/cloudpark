from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone

from core.admin import TicketAdmin
from core.models import Ticket, TicketStatus, Priority
from authentication.models import UserProfile

User = get_user_model()


class TicketAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.ticket_admin = TicketAdmin(Ticket, self.admin_site)
        
        self.superuser = User.objects.create_superuser(
            email='admin@test.com',
            password='testpass123'
        )
        
        self.attendant_user = User.objects.create_user(
            email='atendente@test.com',
            password='testpass123',
            profile=UserProfile.ATTENDANT
        )
        
        self.technician_user = User.objects.create_user(
            email='tecnico@test.com',
            password='testpass123',
            profile=UserProfile.TECHNICIAN
        )
        
        self.ticket_attendant = Ticket.objects.create(
            title='Ticket do Atendente',
            description='Descrição do ticket',
            priority=Priority.MEDIUM,
            status=TicketStatus.OPEN,
            attendant=self.attendant_user
        )

    def _create_request(self, user):
        request = self.factory.get('/')
        request.user = user
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        return request

    def test_list_display(self):
        expected_fields = ['title', 'priority', 'status', 'attendant', 'created_at']
        self.assertEqual(self.ticket_admin.list_display, expected_fields)

    def test_get_fieldsets_creation(self):
        request = self._create_request(self.attendant_user)
        fieldsets = self.ticket_admin.get_fieldsets(request, obj=None)
        
        basic_fields = fieldsets[0][1]['fields']
        self.assertNotIn('attendant', basic_fields)
        
        expected_basic_fields = ('title', 'priority', 'status', 'description')
        self.assertEqual(basic_fields, expected_basic_fields)

    def test_save_model_new_ticket(self):
        request = self._create_request(self.attendant_user)
        ticket = Ticket(
            title='Novo Ticket',
            description='Descrição',
            priority=Priority.LOW,
            status=TicketStatus.OPEN
        )
        
        self.ticket_admin.save_model(request, ticket, None, change=False)
        
        self.assertEqual(ticket.attendant, self.attendant_user)

    def test_get_queryset_superuser(self):
        request = self._create_request(self.superuser)
        queryset = self.ticket_admin.get_queryset(request)
        
        self.assertEqual(queryset.count(), 1)

    def test_get_queryset_normal_user(self):
        request = self._create_request(self.attendant_user)
        queryset = self.ticket_admin.get_queryset(request)
        
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.ticket_attendant)

    def test_has_add_permission_authenticated(self):
        request = self._create_request(self.attendant_user)
        self.assertTrue(self.ticket_admin.has_add_permission(request))

    def test_has_change_permission_own_ticket(self):
        request = self._create_request(self.attendant_user)
        self.assertTrue(self.ticket_admin.has_change_permission(request, self.ticket_attendant))

    def test_has_change_permission_others_ticket(self):
        request = self._create_request(self.attendant_user)
        other_ticket = Ticket.objects.create(
            title='Ticket de Outro Usuário',
            attendant=self.technician_user
        )
        self.assertFalse(self.ticket_admin.has_change_permission(request, other_ticket))


class TicketAdminAttendantRestrictionsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.ticket_admin = TicketAdmin(Ticket, self.admin_site)
        
        self.attendant_user = User.objects.create_user(
            email='atendente@test.com',
            password='testpass123',
            profile=UserProfile.ATTENDANT
        )
        
        self.technician_user = User.objects.create_user(
            email='tecnico@test.com',
            password='testpass123',
            profile=UserProfile.TECHNICIAN
        )
        
        self.ticket = Ticket.objects.create(
            title='Ticket de Teste',
            description='Descrição',
            priority=Priority.MEDIUM,
            status=TicketStatus.OPEN,
            attendant=self.attendant_user
        )

    def _create_request(self, user):
        request = self.factory.get('/')
        request.user = user
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        return request

    def test_get_form_attendant_restricts_resolved(self):
        request = self._create_request(self.attendant_user)
        form = self.ticket_admin.get_form(request, obj=self.ticket)
        
        status_field = form.base_fields.get('status')
        choices = [choice[0] for choice in status_field.choices]
        
        self.assertNotIn(TicketStatus.RESOLVED, choices)
        self.assertIn(TicketStatus.OPEN, choices)

    def test_get_form_technician_has_all_options(self):
        request = self._create_request(self.technician_user)
        form = self.ticket_admin.get_form(request, obj=self.ticket)
        
        status_field = form.base_fields.get('status')
        choices = [choice[0] for choice in status_field.choices]
        
        self.assertIn(TicketStatus.RESOLVED, choices)

    def test_save_model_attendant_cannot_resolve(self):
        request = self._create_request(self.attendant_user)
        
        self.ticket.status = TicketStatus.RESOLVED
        
        self.ticket_admin.save_model(request, self.ticket, None, change=True)
        
        messages = list(request._messages)
        self.assertTrue(any('não podem alterar o status para "Resolvido"' in str(msg) for msg in messages))


class TicketAdminIntegrationTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            email='admin@test.com',
            password='testpass123'
        )
        
        self.attendant_user = User.objects.create_user(
            email='atendente@test.com',
            password='testpass123',
            profile=UserProfile.ATTENDANT,
            is_staff=True
        )
        
        self.ticket = Ticket.objects.create(
            title='Ticket de Integração',
            description='Descrição do ticket',
            priority=Priority.MEDIUM,
            status=TicketStatus.OPEN,
            attendant=self.attendant_user
        )

    def test_admin_list_view_superuser(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('admin:core_ticket_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_admin_add_view_attendant(self):
        self.client.force_login(self.attendant_user)
        response = self.client.get(reverse('admin:core_ticket_add'))
        self.assertEqual(response.status_code, 200)

    def test_admin_change_view_own_ticket(self):
        self.client.force_login(self.attendant_user)
        response = self.client.get(
            reverse('admin:core_ticket_change', args=[self.ticket.pk])
        )
        self.assertEqual(response.status_code, 200) 