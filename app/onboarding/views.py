"""
Onboarding View
"""

from core.models import Onboarding, OnboardingStep
from onboarding import serializers

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'onboardingsteps',
                OpenApiTypes.STR,
                description='Onboarding Steps'
            ),
        ]
    )
)

class OnboardingViewSet(viewsets.ModelViewSet):
    """View for managing Onboarding information"""
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = serializers.OnboardingDetailsSerializer
    # queryset = Onboarding.objects.prefetch_related('onboardingsteps', 'images').select_related('department')
    queryset = Onboarding.objects.prefetch_related('onboardingstep')
    # queryset = Onboarding.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns objects in descending order"""
        return self.queryset.order_by('-id')

    def get_serializer_class(self):
        """Return a serializer class for the request"""
        if self.action == 'list':
            return serializers.OnboardingSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new onboarding """
        if serializer.is_valid():
            serializer.save(user=self.request.user)

class OnboardingStepViewSet(viewsets.ModelViewSet):
    """View for managing Onboarding information"""
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = serializers.OnboardingStepDetailsSerializer
    queryset = OnboardingStep.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns objects in descending order"""
        return self.queryset.order_by('-id')

    def get_serializer_class(self):
        """Return a serializer class for the request"""
        if self.action == 'list':
            return serializers.OnboardingStepSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new onboarding """
        if serializer.is_valid():
            serializer.save(user=self.request.user)
