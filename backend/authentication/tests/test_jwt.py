from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from authentication.models import UserProfile

User = get_user_model()


class JWTAuthenticationTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
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

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'email': 'tecnico@test.com',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'tecnico@test.com')

    def test_login_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'email': 'tecnico@test.com',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_login_missing_credentials(self):
        response = self.client.post(reverse('login'), {
            'email': 'tecnico@test.com'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_refresh_token_success(self):
        login_response = self.client.post(reverse('login'), {
            'email': 'tecnico@test.com',
            'password': 'testpass123'
        })
        
        refresh_token = login_response.data['refresh_token']
        
        response = self.client.post(reverse('refresh'), {
            'refresh_token': refresh_token
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)

    def test_refresh_token_invalid(self):
        response = self.client.post(reverse('refresh'), {
            'refresh_token': 'invalid_token'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_api_access_with_jwt(self):
        login_response = self.client.post(reverse('login'), {
            'email': 'tecnico@test.com',
            'password': 'testpass123'
        })
        
        access_token = login_response.data['access_token']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(reverse('ticket-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_access_without_jwt(self):
        response = self.client.get(reverse('ticket-list'))
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) 