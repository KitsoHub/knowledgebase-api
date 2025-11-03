"""
Test policy api's
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.helpers import create_user
from core.models import Policy, Department
from django.core.files.uploadedfile import SimpleUploadedFile
import os

POLICY_URL = reverse('policy:policy-list')


def create_policy_document(user, **params):
    """ Create and return a policy object"""
    department = Department.objects.create(
        dept_name="HR Department")
    defaults = {
        'title': 'Test Policy',
        'description': 'This is a test policy description.',
        'document_type': 'article',
        'document': 'example2.pdf'
    }
    policy = Policy.objects.create(
        user=user, created_by=user,
        department=department,
        **defaults)

    return policy


def details_url(policy_id):
    """Returns the policy details url"""
    return reverse('policy:policy-detail', args=[policy_id])


class PublicPublisherTests(TestCase):
    """Tests for unauthenticated users"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth required"""
        res = self.client.get(POLICY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
