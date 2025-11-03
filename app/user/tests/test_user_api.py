"""user api tests"""

from django.test import TestCase, tag
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core import helpers


CREATE_USER_API = reverse('user:create')
TOKEN_URL = reverse('user:token')
PROFILE_URL = reverse('user:profile')


@tag('user')
class PublicUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_create_success(self):
        payload = {
            'email': 'testuser@example.com',
            'password': 'testpassword123',
            'name': 'Test Name'}

        res = self.client.post(CREATE_USER_API, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_create_token_success(self):
        """Test create token"""
        user_details = {
            'email': 'testuser@example.com',
            'password': 'testpassword123',
            'name': 'Test Name'
        }

        helpers.create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_profile_access_unathorized_error(self):
        """Test user profile unathorized access"""

        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = helpers.create_user(
            email='testuser@example.com',
            password='testpassword123',
            name='Test Name'
        )

        self.client.force_authenticate(user=self.user)

    def test_retrive_profile_success(self):
        """Test retrieving user profile"""

        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
            'is_staff': self.user.is_staff
        })

    def test_verifier_user_create(self):
        """Test creating a verifier user"""
        self.verifier_email = "verifier_user@example.com"

        user = helpers.create_user(
            email=self.verifier_email,
            password='testpassword123',
            name="Verifier User",
            is_verifier=True,
            is_staff=True,
        )

        self.assertEqual(user.email, self.verifier_email)
        self.assertTrue(user.is_verifier)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_verifier_user_with_manager(self):
        """Test creating a verifier user using the manager method"""
        self.verifier_email = "verifier@example.com"
        user = helpers.create_verifier(
            email=self.verifier_email,
            password='testpassword123', name="Verifier"
        )

        self.assertEqual(user.email, self.verifier_email)
        self.assertTrue(user.is_verifier)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
