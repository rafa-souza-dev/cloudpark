from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from authentication.models import UserProfile
from core.models import Ticket, TicketStatus, Priority

User = get_user_model()


class TicketAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.superuser = User.objects.create_superuser(
            email='admin@test.com',
            password='testpass123'
        )
        
        self.technician = User.objects.create_user(
            email='tecnico@test.com',
            password='testpass123',
            profile=UserProfile.TECHNICIAN
        )
        
        self.attendant = User.objects.create_user(
            email='atendente@test.com',
            password='testpass123',
            profile=UserProfile.ATTENDANT
        )
        
        self.ticket = Ticket.objects.create(
            title='Ticket de Teste',
            description='Descrição do ticket',
            priority=Priority.MEDIUM,
            status=TicketStatus.OPEN,
            attendant=self.attendant
        )

    def test_list_tickets_technician(self):
        self.client.force_authenticate(user=self.technician)
        response = self.client.get(reverse('ticket-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_tickets_attendant(self):
        self.client.force_authenticate(user=self.attendant)
        response = self.client.get(reverse('ticket-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_tickets_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(reverse('ticket-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_by_status(self):
        self.client.force_authenticate(user=self.technician)
        response = self.client.get(reverse('ticket-list'), {'status': 'open'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_by_priority(self):
        self.client.force_authenticate(user=self.technician)
        response = self.client.get(reverse('ticket-list'), {'priority': 'medium'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_tickets(self):
        self.client.force_authenticate(user=self.technician)
        response = self.client.get(reverse('ticket-list'), {'search': 'Teste'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_update_status_technician_success(self):
        self.client.force_authenticate(user=self.technician)
        url = reverse('ticket-update-status', args=[self.ticket.pk])
        response = self.client.patch(url, {'status': 'in_progress'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, TicketStatus.IN_PROGRESS)

    def test_update_status_attendant_forbidden(self):
        self.client.force_authenticate(user=self.attendant)
        url = reverse('ticket-update-status', args=[self.ticket.pk])
        response = self.client.patch(url, {'status': 'in_progress'})
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_status_invalid_transition(self):
        self.client.force_authenticate(user=self.technician)
        url = reverse('ticket-update-status', args=[self.ticket.pk])
        response = self.client.patch(url, {'status': 'resolved'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_status_valid_transition(self):
        self.ticket.status = TicketStatus.IN_PROGRESS
        self.ticket.save()
        
        self.client.force_authenticate(user=self.technician)
        url = reverse('ticket-update-status', args=[self.ticket.pk])
        response = self.client.patch(url, {'status': 'resolved'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, TicketStatus.RESOLVED)

    def test_retrieve_ticket(self):
        self.client.force_authenticate(user=self.technician)
        response = self.client.get(reverse('ticket-detail', args=[self.ticket.pk]))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Ticket de Teste')
        self.assertEqual(response.data['status'], 'open')
        self.assertEqual(response.data['status_display'], 'Aberto') 