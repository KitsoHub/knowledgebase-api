from django.core.management import call_command
from django.contrib.auth.models import Group, Permission
from django.test import SimpleTestCase
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from core.helpers import create_user
from django.urls import reverse

ARTIFACTS_URL = reverse('artifacts:artifacts-list')

class SetUpRoleCommandTest(TestCase):
    """Test SetUpRoleCommand"""

    def test_command_fails_with_missing_permissions(self):
        """Test SetUpRoleCommand fails when permission does not exist"""

        Permission.objects.filter(codename='view_artifacts').delete()

        self.assertFalse(Permission.objects.filter(
            codename='view_artifacts').exists())

        with self.assertRaises(ValueError) as context:
            call_command('set_up_roles')

        self.assertIn("Missing permissions: {'view_artifacts'}",
                      str(context.exception))

    def test_command_creates_group_and_permissions(self):
        """Test for creating a group and permissions for the Artifact Publisher"""
        call_command('set_up_roles')
        group = Group.objects.get(name='ArtifactPublisher')

        expected_permissions = {"view_artifacts",
                                "view_artifactimages", "change_artifacts"}
        assigned_permissions = set(
            group.permissions.values_list('codename', flat=True))

        self.assertEqual(assigned_permissions, expected_permissions)


class SetUpRoleAPITests(TestCase):
    """Test API permissions enforcement"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='publisheruser@example.com',
            password='testpassword123'
        )
        self.user_without_permission = create_user(
            email="normaluser@example.com", password="testpass")


        # TODO: refactor to use command
        self.publisher_group = Group.objects.get_or_create(
            name="ArtifactPublisher")[0]

        publisher_permissions = Permission.objects.filter(
            codename__in=["view_artifacts", "view_artifactimages", "change_artifacts"])
        self.publisher_group.permissions.set(publisher_permissions)
        self.user.groups.add(self.publisher_group)

    def test_user_without_permission_cannot_access_api(self):
        self.client.login(email="normaluser@example.com",
                          password="testpass")

        res = self.client.get(ARTIFACTS_URL)

        # TODO: this access assumes is_authenticated and not the group
        # HTTP_403_FORBIDDEN is required here
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_with_permission_can_access_api(self):
        self.client.force_authenticate(self.user)

        res = self.client.get(ARTIFACTS_URL)

        # TODO: this access assumes is_authenticated and not the group

        self.assertEqual(res.status_code, status.HTTP_200_OK)
