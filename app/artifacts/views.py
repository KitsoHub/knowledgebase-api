"""
Artifacts View
"""

from core.models import Artifacts
from artifacts import serializers

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser


class ArtifactsViewSet(viewsets.ModelViewSet):
    """View for managing artifact information"""
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = serializers.ArtifactsDetailsSerializer
    queryset = Artifacts.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns artifact objects in descending order"""
        return self.queryset.order_by('-id')

    def get_serializer_class(self):
        """Return a serializer class for the request"""
        if self.action == 'list':
            return serializers.ArtifactsSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new artifact"""
        if serializer.is_valid():
            serializer.save(user=self.request.user)
