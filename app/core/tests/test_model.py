"""Tests for models"""

from django.test import TestCase, tag
from core import models
from core.helpers import (get_user_model, create_user)


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
