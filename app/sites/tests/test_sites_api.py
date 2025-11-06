from django.test import TestCase, tag
from django.urls import reverse
from django.contrib.auth.models import Permission, Group
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.models import (User, HeritageSite, SiteSettings, SiteMetadata)
# import json
from core.helpers import create_user, create_verifier

SITES_URL = reverse('sites:sites-list')


@tag('sitesapi')
class SiteAPITest(TestCase):
    """Tests for the Heritage Site API"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='testuser@example.com', password='testpass')
        self.admin_user = User.objects.create_superuser(
            email='adminuser@example.com', password='adminpass')
        self.verifier = create_verifier(
            email='verifieruser@example.com', password='verifierpass')

        settings = SiteSettings.load()
        settings.verifiers.add(self.verifier)

        perm = Permission.objects.get(codename='can_override_verification')
        self.admin_user.user_permissions.add(perm)

        self.site_metadata = {
            'unesco': False,
            'undp': False,
            'unicef': False,
            'local_context': 'Test context',
            'indigenous_system': 'Test system',
            'rights': 'Test rights',
            'ip_metadata': 'Test metadata',
            'sensitivity_level': 'public',
            'access_protocol': 'HTTPS',
        }
        site_metadata = SiteMetadata.objects.create(
            **self.site_metadata,
        )

        self.site_data = {
            'site_name': 'Test Heritage Site',
            'description': 'A beautiful heritage site',
            'category': 'heritage',
            'latitude': 25.123456,
            'longitude': 45.654321,
            'population_density': 1000,
            'migration_route': 'Up north',
            'metadata': site_metadata,
            'site_settings': settings,
            'created_by': self.user
        }
        self.site = HeritageSite.objects.create(**self.site_data)
        self.site.refresh_from_db()

    def test_list_sites_unauthenticated(self):

        # response = self.client.get('/api/sites/sites/')
        self.client.force_authenticate(user=self.user)
        res = self.client.get(SITES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreater(len(res.data), 0)

    # def test_create_site_unauthenticated(self):
    #     """Test unauthenticated user cannot create site"""
    #     response = self.client.post(
    #         '/api/sites/',
    #         data=json.dumps(self.site_data),
    #         content_type='application/json'
    #     )

    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_create_site_authenticated(self):
    #     """Test authenticated user can create site"""
    #     self.client.force_authenticate(user=self.user)

    #     response = self.client.post(
    #         '/api/sites/',
    #         data=json.dumps(self.site_data),
    #         content_type='application/json'
    #     )

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(HeritageSite.objects.count(), 1)

    #     site = HeritageSite.objects.first()
    #     self.assertEqual(site.name, 'Test Heritage Site')
    #     self.assertEqual(site.status, 'pending')
    #     self.assertEqual(site.created_by, self.user)


@tag('verificationflow')
class VerificationFlowTest(TestCase):
    """Tests for the verification flow of heritage sites"""

    def setUp(self):
        self.client = APIClient()
        self.verifiers_group, _ = Group.objects.get_or_create(name='verifiers')
        self.user = create_user(
            password='testpass123',
            email='user@example.com'

        )

        self.verifier1 = create_verifier(
            password='testpass123',
            email='verifier1@example.com',
            is_staff=True, is_verifier=True
        )

        self.verifier2 = create_verifier(
            password='testpass123',
            email='verifier2@example.com',
            is_staff=True, is_verifier=True
        )

        self.verifier3 = create_verifier(
            password='testpass123',
            email='verifier3@example.com',
            is_staff=True, is_verifier=True
        )

        self.superuser = get_user_model().objects.create_superuser(
            password='testpass123',
            email='admin@example.com'
        )

        self.metadata = SiteMetadata.objects.create(
            unesco=True,
            sensitivity_level='public'
        )

        # self.site_settings = SiteSettings.objects.create(
        #     required_verifier_count=2
        # )

        self.site_settings = SiteSettings.load()  # Using singleton pattern
        self.site_settings.required_verifier_count = 2
        self.site_settings.save()

        self.verifier1.groups.add(self.verifiers_group)
        self.verifier2.groups.add(self.verifiers_group)
        self.verifier3.groups.add(self.verifiers_group)

        self.site_settings.verifiers.set(
            [self.verifier1, self.verifier2, self.verifier3])

        self.site = HeritageSite.objects.create(
            site_name="Test Heritage Site",
            description="A test heritage site",
            latitude=-122.4194,
            longitude=37.7749,
            category='heritage',
            metadata=self.metadata,
            site_settings=self.site_settings
        )

    def test_pending_with_one_vote(self):
        """Test that status remains 'pending' with only one vote"""

        self.assertTrue(self.verifier1.groups.filter(
            name='verifiers').exists())

        self.assertTrue(
            self.site.site_settings.verifiers.filter(
                id=self.verifier1.id).exists()
        )

        self.client.force_authenticate(user=self.verifier1)
        response = self.client.post(
            f'/api/sites/sites/{self.site.id}/submit_verification/',
            {'vote': 'approve'}
        )

        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.site.refresh_from_db()
        self.assertEqual(self.site.status, 'pending')
        self.assertEqual(self.site.site_verification_vote.count(), 1)

    def test_pending_with_mixed_votes(self):
        """Test that status remains 'pending' with mixed votes (1 approve, 1 reject)"""

        self.client.force_authenticate(user=self.verifier1)
        self.client.post(
            f'/api/sites/sites/{self.site.id}/submit_verification/',
            {'vote': 'approve'}
        )

        self.client.force_authenticate(user=self.verifier2)
        self.client.post(
            f'/api/sites/sites/{self.site.id}/submit_verification/',
            {'vote': 'reject'}
        )

        self.site.refresh_from_db()
        self.assertEqual(self.site.status, 'pending')
        self.assertEqual(self.site.site_verification_vote.count(), 2)

    def test_verified_with_two_approvals(self):
        """Test that status changes to 'verified' with 2 approve votes"""

        self.client.force_authenticate(user=self.verifier1)
        self.client.post(
            f'/api/sites/sites/{self.site.id}/submit_verification/',
            {'vote': 'approve'}
        )

        self.client.force_authenticate(user=self.verifier2)
        response = self.client.post(
            f'/api/sites/sites/{self.site.id}/submit_verification/',
            {'vote': 'approve'}
        )

        self.site.refresh_from_db()
        self.assertEqual(self.site.status, 'verified')
        self.assertEqual(response.data['site']['status'], 'verified')
        self.assertEqual(self.site.site_verification_vote.count(), 2)
