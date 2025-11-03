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

    def test_create_artifact_success(self):
        """Test creating artifacts model"""

        user = create_user(
            email='test@example.com',
            password='testpass123'
        )
        # TODO: add relation to culture, site, ethnic group
        artifact = models.Artifacts.objects.create(
            user=user,
            artifact_name='Test Artifact',
            artifact_type='tool',
            description='Test Artifact Description',
            historical_significance=5.0,
            cultural_significance=5.0,
            submission_date='2024-10-10',
            status='pending',

        )

        self.assertEqual(str(artifact), artifact.artifact_name)

# Images
    def test_create_artifact_imgs(self):
        """Test creating artifact images"""

        user = create_user(
            email='test@example.com',
            password='testpass123'
        )

        self.artifact_data = models.Artifacts.objects.create(
            user=user,
            artifact_name='Test Artifact Images',
            artifact_type='tool',
            description='Test Artifact Description Images',
        )

        artifact_imgs = models.ArtifactImages.objects.create(
            artifact=self.artifact_data,
            images='artifact_example.jpg'
        )
        path = '/vol/web/media/artifact_example.jpg'
        self.assertEqual(artifact_imgs.artifact, self.artifact_data)
        self.assertEqual(artifact_imgs.images.path, f'{path}')

    def test_create_artifact_status_log(self):
        """Test creating artifacts status log model"""

        user = create_user(
            email='test@example.com',
            password='testpass123'
        )
        # TODO: add relation to culture, site, ethnic group
        artifact = models.Artifacts.objects.create(
            user=user,
            artifact_name='Test Artifact',
            artifact_type='tool',
            description='Test Artifact Description',
            historical_significance=5.0,
            cultural_significance=5.0,
            submission_date='2024-10-10',
            status='pending',

        )

        logs = models.ArtifactStatusLog.objects.filter(artifact=artifact.id)
        self.assertEqual(len(logs), 1)
