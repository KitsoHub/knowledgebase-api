"""Policy serializer"""
import os
from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers
from core.models import Policy


class PolicySerializer(serializers.ModelSerializer):
    """ Policy serializer"""

    class Meta:
        model = Policy
        fields = ['id', 'title', 'description', 'document']
        read_only_fields = ['id']


class PolicyDetailsSerializer(PolicySerializer):
    class Meta(PolicySerializer.Meta):
        fields = PolicySerializer.Meta.fields + ['created_at', 'updated_at']
