"""Tests for models"""

from django.test import TestCase, tag
from core import models
from core.helpers import (get_user_model, create_user)
from core import helpers


class ModelTests(TestCase):
    """Model tests"""

    def test_create_user_successful(self):
        """creating a user"""

        email = "test5@example.com"
        password = "testpass123"
        user = create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_email_normalized(self):
        """test normalized password"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'pass123')
            self.assertEqual(user.email, expected)

    def test_user_without_email_raise_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testpassword123')

    def test_creating_superuser(self):
        user = get_user_model().objects.create_superuser(
            'admin@example.com', 'testpassword123'
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_onboarding_success(self):
        """Test creating Onboarding model"""

        user = create_user(
            email='test@example.com',
            password='testpass123'
        )

        self.department = models.Department.objects.create(
            dept_name="HR Department")
        onboarding = models.Onboarding.objects.create(
            user=user,
            notes='Test Onboarding',
            onboarding_type='operations',
            created_at='2024-10-10',
            updated_at='2024-10-10',
            status='draft',

        )

        self.assertEqual(str(onboarding),
                         f'{onboarding.user} {onboarding.status}')

# Images
    def test_create_onboarding_imgs(self):
        """Test creating onboarding images"""

        user = create_user(
            email='test@example.com',
            password='testpass123'
        )

        self.onboarding_data = models.Onboarding.objects.create(
            user=user,
            onboarding_name='Test Onboarding Images',
            onboarding_type='tool',
        )

        onboarding_imgs = models.OnboardingNoteImages.objects.create(
            note=self.onboarding_data,
            images='onboarding_example.jpg'
        )
        path = '/vol/web/media/onboarding_example.jpg'
        self.assertEqual(onboarding_imgs.note, self.onboarding_data)
        self.assertEqual(onboarding_imgs.images.path, f'{path}')

    def test_create_policy_success(self):
        """Test creating Policy model"""

        user = create_user(
            email='test@example.com',
            password='testpass123'
        )
        department = models.Department.objects.create(
            dept_name="HR Department")

        policy = models.Policy.objects.create(
            user=user,
            title='Test Policy',
            description='This is a test policy description.',
            created_by=user,
            department=department,
            document_type='article'
        )

        self.assertEqual(policy.title, 'Test Policy')
        self.assertEqual(policy.created_by.email, user.email)
        self.assertEqual(models.Policy.objects.all().count(), 1)

# Site Metadata


class SiteSettingsModelTest(TestCase):
    """Test SiteSettings singleton model"""

    def test_singleton_pattern(self):
        """Test that only one settings instance exists"""
        settings1 = models.SiteSettings.load()
        settings2 = models.SiteSettings.load()

        self.assertEqual(settings1.pk, settings2.pk)
        self.assertEqual(models.SiteSettings.objects.count(), 1)

    def test_default_verifier_count(self):
        """Test default required verifier count"""
        settings = models.SiteSettings.load()
        self.assertEqual(settings.required_verifier_count, 2)

    def test_add_verifiers(self):
        """Test adding verifiers to settings"""
        settings = models.SiteSettings.load()
        self.verifier_email_1 = "verifier1@example.com"
        self.verifier_email_2 = "verifier2@example.com"
        user1 = helpers.create_verifier(
            email=self.verifier_email_1,
            password='testpassword123', name="Verifier1"
        )
        user2 = helpers.create_verifier(
            email=self.verifier_email_2,
            password='testpassword123', name="Verifier2"
        )

        settings.verifiers.add(user1, user2)

        self.assertEqual(settings.verifiers.count(), 2)
        self.assertIn(user1, settings.verifiers.all())
        self.assertIn(user2, settings.verifiers.all())


class SiteMetadataModelTests(TestCase):

    """Tests for SiteMetadata model"""

    def setUp(self):
        email = "test5@example.com"
        password = "testpass123"
        self.user = create_user(email=email, password=password)
        self.assertEqual(self.user.email, email)
        self.assertTrue(self.user.check_password(password))

    def test_create_site(self):
        """Test basic site creation"""

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

        site_metadata = models.SiteMetadata.objects.create(
            **self.site_metadata,
        )

        # Create site settings with 2 required verifiers
        self.site_settings = models.SiteSettings.objects.create(
            required_verifier_count=2
        )
        self.verifier_email_2 = "verifier2@example.com"
        self.verifier_email_3 = "verifier3@example.com"
        self.verifier2 = helpers.create_verifier(
            email=self.verifier_email_2,
            password='testpassword123', name="Verifier2"
        )
        self.verifier3 = helpers.create_verifier(
            email=self.verifier_email_3,
            password='testpassword123', name="Verifier3"
        )

        # self.site_settings.verifiers.add(user1, user2)
        self.site_settings.verifiers.set(
            [self.verifier2, self.verifier3])

        site_data = {
            'site_name': 'Test Heritage Site',
            'description': 'A test site description',
            'category': 'heritage',
            'latitude': 25.123456,
            'longitude': 45.654321,
            'population_density': 1000,
            'migration_route': 'Test migration routes',
            'metadata': site_metadata,
            'site_settings': self.site_settings,
            'created_by': self.user
        }
        site = models.HeritageSite.objects.create(**site_data)

        self.assertEqual(site.site_name, 'Test Heritage Site')
        self.assertEqual(site.status, 'pending')
        self.assertEqual(site.category, 'heritage')
        self.assertIsNotNone(site.date_created)
        self.assertIsNotNone(site.last_updated)


@tag('verification')
class VerificationModelTest(TestCase):
    """Test Verification model functionality"""

    def setUp(self):
        email = "test5@example.com"
        password = "testpass123"
        self.user = create_user(email=email, password=password)
        self.assertEqual(self.user.email, email)
        self.assertTrue(self.user.check_password(password))

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

        site_metadata = models.SiteMetadata.objects.create(
            **self.site_metadata,
        )

        # Create site settings with 2 required verifiers
        self.site_settings = models.SiteSettings.objects.create(
            required_verifier_count=2
        )
        self.verifier_email_2 = "verifier2@example.com"
        self.verifier_email_3 = "verifier3@example.com"
        self.verifier2 = helpers.create_verifier(
            email=self.verifier_email_2,
            password='testpassword123', name="Verifier2"
        )
        self.verifier3 = helpers.create_verifier(
            email=self.verifier_email_3,
            password='testpassword123', name="Verifier3"
        )

        # self.site_settings.verifiers.add(user1, user2)
        self.site_settings.verifiers.set(
            [self.verifier2, self.verifier3])

        self.site_data = {
            'site_name': 'Test Heritage Site 2',
            'description': 'A test site description',
            'category': 'heritage',
            'latitude': 25.123456,
            'longitude': 45.654321,
            'population_density': 1000,
            'migration_route': 'Test migration routes',
            'metadata': site_metadata,
            'site_settings': self.site_settings,
            'created_by': self.user
        }
        self.site = models.HeritageSite.objects.create(**self.site_data)

    def test_create_verification(self):
        """Test verification creation"""
        verification = models.SiteVerificationVote.objects.create(
            site=self.site,
            verifier=self.verifier2,
            vote='approve',
            comment='Looks good'
        )

        self.assertEqual(verification.site, self.site)
        self.assertEqual(verification.verifier, self.verifier2)
        self.assertEqual(verification.vote, 'approve')
        self.assertIsNotNone(verification.created_at)

    def test_verification_unique_constraint(self):
        """Test that verifier can only vote once per site"""
        models.SiteVerificationVote.objects.create(
            site=self.site,
            verifier=self.verifier2,
            vote='approve'
        )

        with self.assertRaises(Exception):  # IntegrityError
            models.SiteVerificationVote.objects.create(
                site=self.site,
                verifier=self.verifier2,
                vote='reject'
            )
