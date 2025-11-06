
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from sites.permission import IsVerifier
from sites.services import VerificationService
from rest_framework.decorators import action
from django.db.models import Q
# from rest_framework.parsers import MultiPartParser, FormParser
# from django_filters.rest_framework import DjangoFilterBackend
from core.models import HeritageSite, SiteVerificationVote
from sites.serializers import (SiteListSerializer, SiteCreateUpdateSerializer,
                               SiteDetailSerializer, SiteVerificationVoteSerializer as VerificationVoteSerializer,
                               VoteSubmissionSerializer)


class HeritageSiteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Site CRUD operations and verification workflow.

    List/Retrieve: Anyone can view
    Create: Authenticated users
    Update/Delete: Owner only
    Verify: Verifiers only
    Override: Admins only
    """
    queryset = HeritageSite.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    search_fields = ['site_name', 'description']
    ordering_fields = ['date_created', 'last_updated', 'site_name']
    ordering = ['-date_created']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return SiteListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SiteCreateUpdateSerializer
        return SiteDetailSerializer

    def get_queryset(self):
        # queryset = HeritageSite.objects.select_related('created_by').prefetch_related(
        #     'verifications',
        #     'verifications__verifier',
        #     'verification_logs'
        # )
        queryset = HeritageSite.objects.select_related('created_by')

        if not self.request.user.is_authenticated or not self.request.user.is_staff:
            queryset = queryset.filter(metadata__sensitivity_level='public')

        return queryset

    def perform_create(self, serializer):
        """create a new site with the logged in user as creator"""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsVerifier])
    def submit_verification(self, request, pk=None):
        """
        Submit a verification vote for a site.

        POST /api/sites/{id}/submit_verification/
        Body: {"vote": "approve|reject", "comment": "..."}
        """
        site = self.get_object()
        serializer = VoteSubmissionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            verification = VerificationService.process_vote(
                site=site,
                verifier=request.user,
                vote=serializer.validated_data['vote'],
                comment=serializer.validated_data.get('comment', '')
            )

            # Return updated site with verification status
            site.refresh_from_db()
            response_serializer = SiteDetailSerializer(
                site, context={'request': request})

            return Response({
                'message': 'Vote submitted successfully',
                'verification': VerificationVoteSerializer(verification).data,
                'site': response_serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class VerificationVoteViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for verification votes (read-only)"""
    queryset = SiteVerificationVote.objects.all()
    serializer_class = VerificationVoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter votes to only those the user can access"""
        user = self.request.user
        if user.is_superuser:
            return SiteVerificationVote.objects.all()
        return SiteVerificationVote.objects.filter(
            Q(verifier=user) | Q(site__site_settings__verifiers=user)
        ).distinct()
