from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.helpers import create_user, get_image
from core.models import (
    Artifacts, ArtifactImages, ArtifactStatus, ArtifactStatusLog)
from artifacts.serializers import (
    ArtifactsSerializer,
    ArtifactsDetailsSerializer)
import os


ARTIFACTS_URL = reverse('artifacts:artifacts-list')


def create_artifact(user, **params):
    defaults = {
        'artifact_name': 'Test Artifact',
        'artifact_type': 'tool',
        'description': 'Test description',
        'historical_significance': 5.0,
        'cultural_significance': 5.0,
    }

    defaults.update(params)
    artifact = Artifacts.objects.create(user=user, **defaults)
    return artifact


def details_url(artifact_id):
    """returns the details url"""
    return reverse('artifacts:artifacts-detail', args=[artifact_id])


class PublicArtifactAPITests(TestCase):
    """Tests for unauthenticated user"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication required"""
        res = self.client.get(ARTIFACTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateArtifactAPITests(TestCase):
    """Tests for authenticated users"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='testuser@example.com',
            password='testpassword123'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_artifact(self):
        """Retrieve artifacts"""
        create_artifact(user=self.user)
        create_artifact(user=self.user)

        res = self.client.get(ARTIFACTS_URL)
        artifact_data = Artifacts.objects.all().order_by('-id')
        serializer = ArtifactsSerializer(artifact_data, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_create_artifact(self):
        payload = {
            'artifact_name': 'Test Artifact',
            'artifact_type': 'tool',
            'description': 'Test description',
            'historical_significance': 5.0,
            'cultural_significance': 5.0
        }

        res = self.client.post(ARTIFACTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        artifact_data = Artifacts.objects.get(id=res.data['id'])
        self.assertEqual(self.user, artifact_data.user)
        self.assertEqual(payload['artifact_name'], artifact_data.artifact_name)

    def test_get_artifact_details(self):
        """Get the details of an artifact"""
        artifact_data = create_artifact(user=self.user)
        url = details_url(artifact_data.id)
        res = self.client.get(url)

        serializer = ArtifactsDetailsSerializer(artifact_data)
        self.assertEqual(res.data, serializer.data)

    def test_delete_artifact(self):
        """deleting an artifact"""
        artifact_data = create_artifact(user=self.user)
        url = details_url(artifact_data.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Artifacts.objects.filter(
            id=artifact_data.id).exists())

    def test_partial_artifact_update(self):
        """Test partial artifact update"""
        artifact_data = create_artifact(user=self.user)
        url = details_url(artifact_data.id)
        payload = {
            'artifact_name': 'Test Update',
            'artifact_type': 'other'
        }

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        artifact_data.refresh_from_db()
        self.assertEqual(payload['artifact_type'], artifact_data.artifact_type)


def test_full_artifact_update(self):
    artifact_data = create_artifact(user=self.user)
    url = details_url(artifact_data.id)
    payload = {
        'artifact_name': 'Test Artifact Update',
        'artifact_type': 'clothing',
        'description': 'Test description update',
        'historical_significance': 1.0,
        'cultural_significance': 1.0
    }

    res = self.client.patch(url, payload)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    artifact_data.refresh_from_db()
    self.assertEqual(payload['artifact_type'], artifact_data.artifact_type)


class ArtifactImagesAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='testuser@example.com',
            password='testpassword123'
        )

        self.client.force_authenticate(self.user)
        self.artifact = create_artifact(user=self.user)

    def test_img_upload_new_artifact_success(self):
        """Test upload image with new artifact"""
        payload = {
            'artifact_name': 'Test Artifact',
            'artifact_type': 'tool',
            'description': 'Test description',
            'historical_significance': 5.0,
            'cultural_significance': 5.0,
            'uploaded_images': [get_image(), get_image()]
        }

        res = self.client.post(ARTIFACTS_URL, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        artifact_imgs = ArtifactImages.objects.filter(
            artifact_id=res.data['id']
        )

        self.assertIn('images', res.data)
        self.assertTrue(os.path.exists(artifact_imgs[0].images.path))

    def test_img_existing_artifact_success(self):
        """Test that an existing artifact can be updated with new images"""
        url = details_url(self.artifact.id)
        payload = {
            'uploaded_images': [get_image(), get_image()]
        }

        res = self.client.patch(url, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class PrivateArtifactWorkflowTest(TestCase):
    """Tests for Artifact workflow"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='testuser@example.com',
            password='testpassword123'
        )

        self.client.force_authenticate(self.user)
        self.artifact = create_artifact(user=self.user)

    def test_valid_initial_stage(self):
        """Test valid initial stage."""
        log = ArtifactStatusLog.objects.filter(artifact=self.artifact).first()
        self.assertIsNotNone(log)
        self.assertIsNone(log.previous_status)
        self.assertEqual(log.new_status, "draft")

    # def test_invalid_transition_to_published_from_draft(self):
    #     """Test invalid direct transition from pending to published"""
    #     with self.assertRaises(ValueError):
    #         self.artifact.status = 'published'
    #         self.artifact.save()

    def test_valid_initial_to_vetting_transition(self):
        """Test valid initial transition to vetting"""

        artifact_data = create_artifact(user=self.user)
        self.vetter_email = "vetter_user@example.com"

        vetter_user = create_user(
            email=self.vetter_email,
            password='testpassword123',
            name="Vetter User",
            is_vetter=True,
            is_staff=True,
        )
        self.client.force_authenticate(vetter_user)

        url = details_url(artifact_data.id)
        payload = {
            'status': 'vetting',
            'vetted_by': f'{vetter_user.id}'
        }

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        artifact_data.refresh_from_db()

        self.assertEqual(artifact_data.status, 'vetting')

        self.assertEqual(
            artifact_data.vetted_by.email, vetter_user.email)

    def test_valid_vetting_to_verified_transition(self):
        """Test valid transition to verification"""

        artifact_data = create_artifact(user=self.user)
        self.vetter_email = "vetter_user@example.com"
        self.verifier_email = "verifier_user@example.com"
    #    TODO: create a class that will help create auth users
        vetter_user = create_user(
            email=self.vetter_email,
            password='testpassword123',
            name="Vetter User",
            is_vetter=True,
            is_staff=True,
        )
        verifier_user = create_user(
            email=self.verifier_email,
            password='testpassword123',
            name="Verifier User",
            is_verifier=True,
            is_staff=True,
        )
        # vetting phase
        self.client.force_authenticate(vetter_user)
        url = details_url(artifact_data.id)
        payload = {
            'status': 'vetting',
            'vetted_by': f'{vetter_user.id}'
        }

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        artifact_data.refresh_from_db()

        self.assertEqual(artifact_data.status, 'vetting')
        # verification phase
        self.client.force_authenticate(verifier_user)
        url = details_url(artifact_data.id)
        payload = {
            'status': 'verified',
            'verified_by': f'{verifier_user.id}'
        }

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        artifact_data.refresh_from_db()

        self.assertEqual(artifact_data.status, 'verified')

# publishing
    def test_valid_initial_to_published_transition(self):
        """Test valid transition to verification"""

        artifact_data = create_artifact(user=self.user)
        self.vetter_email = "vetter_user@example.com"
        self.verifier_email = "verifier_user@example.com"
        self.publisher_email = "publisher_user@example.com"
    #    TODO: create a class that will help create auth users
        vetter_user = create_user(
            email=self.vetter_email,
            password='testpassword123',
            name="Vetter User",
            is_vetter=True,
            is_staff=True,
        )
        verifier_user = create_user(
            email=self.verifier_email,
            password='testpassword123',
            name="Verifier User",
            is_verifier=True,
            is_staff=True,
        )
        publisher_user = create_user(
            email=self.publisher_email,
            password='testpassword123',
            name="Publisher User",
            is_publisher=True,
            is_staff=True,
        )
        # vetting phase
        self.client.force_authenticate(vetter_user)
        url = details_url(artifact_data.id)
        payload = {
            'status': 'vetting',
            'vetted_by': f'{vetter_user.id}'
        }

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        artifact_data.refresh_from_db()

        self.assertEqual(artifact_data.status, 'vetting')
        # verification phase
        self.client.force_authenticate(verifier_user)
        url = details_url(artifact_data.id)
        payload = {
            'status': 'verified',
            'verified_by': f'{verifier_user.id}'
        }

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        artifact_data.refresh_from_db()

        self.assertEqual(artifact_data.status, 'verified')
        # publish phase
        self.client.force_authenticate(publisher_user)
        url = details_url(artifact_data.id)
        payload = {
            'status': 'published',
            'published_by': f'{verifier_user.id}'
        }

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        artifact_data.refresh_from_db()

        self.assertEqual(artifact_data.status, 'published')

# TODO: Test the list view of artifacts for each role eg- publisher should only see objects with status=verified + published
# TODO: Implement a service class to handle creating an artifact through different stages using different functions.
    #     # TODO: implement a signal to handle verification_date
    #     # self.assertIsNotNone(self.artifact.verification_date)
    # def test_vetting_artifact_updates_published_date(self):
    #     """Test valid initial transition to vetting"""

    #     artifact_data = create_artifact(user=self.user)
    #     self.verifier_email = "verifier_user@example.com"

    #     verifier_user = create_user(
    #         email=self.verifier_email,
    #         password='testpassword123',
    #         name="Verifier User",
    #         is_verifier=True,
    #         is_staff=True,
    #     )
    #     self.client.force_authenticate(verifier_user)

    #     url = details_url(artifact_data.id)
    #     payload = {
    #         'status': 'verified',
    #         'verified_by': f'{verifier_user.id}',
    #         }

    #     res = self.client.patch(url, payload)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)

    #     artifact_data.refresh_from_db()

    #     self.assertEqual(artifact_data.status, 'verified')
    #     self.assertEqual(
    #         artifact_data.verified_by.email, verifier_user.email)
    #     self.assertIsNotNone(artifact_data.verification_date)

    # def test_initial_status_log(self):
    #     """Test that an initial status log is created on artifact creation"""

    #     log = ArtifactStatusLog.objects.filter(artifact=self.artifact).first()
    #     self.assertIsNotNone(log)
    #     self.assertIsNone(log.previous_status)
    #     self.assertEqual(log.new_status, "draft")
    # def test_valid_transition_to_vetting(self):
    #     # self.artifact.status = ArtifactStatus.VETTING

    #     self.verifier_email = "verifier3@example.com"

    #     verifier_user = create_user(
    #         email=self.verifier_email,
    #         password='testpassword123',
    #         name="Verifier User",
    #         is_verifier=True,
    #         is_staff=True,
    #     )
    #     self.client.force_authenticate(verifier_user)

    #     url = details_url(self.artifact.id)
    #     payload = {
    #         'status': 'verified',
    #         'verified_by': f'{verifier_user.id}',
    #         }

    #     res = self.client.patch(url, payload)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)

    #     self.artifact.refresh_from_db()

    #     self.assertEqual(self.artifact.status, ArtifactStatus.VETTING.value)
    #     log = ArtifactStatusLog.objects.last()
    #     breakpoint()
    #     self.assertEqual(log.previous_status, ArtifactStatus.DRAFT.value)
    #     self.assertEqual(log.new_status, ArtifactStatus.VETTING.value)
    #     self.assertEqual(log.changed_by, self.user)

# TODO
# test_only_vetting_role_can_update_to_verified
# test_verification_date_not_reset_for_verified_artifact
# test_transition_to_published
# test_invalid_transition_from_pending_to_published
# test_only_valid_transitions_allowed
# test_transition_to_published_requires_two_vetting_users
# test-RBAC test
