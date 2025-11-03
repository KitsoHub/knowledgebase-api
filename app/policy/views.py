"""
View for policy
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from core.models import Policy
from policy import serializers


class PolicyViewSet(viewsets.ModelViewSet):
    """ PolicyViewSet for managing policies"""
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = serializers.PolicyDetailsSerializer
    queryset = Policy.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.order_by('-id')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PolicySerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """create a new policy"""
        serializer.save(user=self.request.user)
