
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from sites.permission import IsVerifier, IsSuperAdminOrReadOnly
from sites.services import VerificationService
from rest_framework.decorators import action
from django.db.models import Q
# from rest_framework.parsers import MultiPartParser, FormParser
# from django_filters.rest_framework import DjangoFilterBackend
from core.models import HeritageSite, SiteVerificationVote, VerificationLog
from sites.serializers import (SiteListSerializer, SiteCreateUpdateSerializer,
                               SiteDetailSerializer, SiteVerificationVoteSerializer as VerificationVoteSerializer,
                               VoteSubmissionSerializer, AdminOverrideSerializer, SiteVerificationLogSerializer)
from core.parsers import NestedMultipartParser
from rest_framework.parsers import JSONParser


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
    # Use default parsers including NestedMultipartParser
    parser_classes = (JSONParser, NestedMultipartParser,)

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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsSuperAdminOrReadOnly])
    def override_status(self, request, pk=None):
        """Superadmin-only endpoint to override verification status"""
        site = self.get_object()
        serializer = AdminOverrideSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            VerificationService.admin_override(
                site=site,
                new_status=serializer.validated_data['new_status'],
                admin_user=request.user,
                reason=serializer.validated_data.get('reason', '')
            )
            # Return updated site data
            site.refresh_from_db()
            return Response(SiteDetailSerializer(site).data)
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
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Filter votes to only those the user can access"""
        user = self.request.user

        # queryset = SiteVerificationVote.objects.all()
        # # site_id = self.kwargs['pk']

        # if user.is_verifier:
        #     queryset = queryset.order_by('-created_at')
        # return queryset
        if user.is_verifier or user.is_superuser:
            return SiteVerificationVote.objects.all()
        return SiteVerificationVote.objects.filter(
            Q(verifier=user) | Q(site__site_settings__verifiers=user)
        ).distinct()

    @action(detail=True, methods=["get"], url_path="site", permission_classes=[IsAuthenticated, IsVerifier])
    def by_site(self, request, pk=None):
        """
        Return all votes for a given site, or filter by user.
        """
        site_id = pk

        queryset = SiteVerificationVote.objects.filter(site_id=site_id)
        # print("User:>>>>>>>>>>>>", user)

        # user = request.user
        # TODO: fetch base on individual votes
        # Optional: filter by ?user=<id>
        user_id = request.query_params.get("user")
        if user_id:
            queryset = queryset.order_by('-created_at')

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SiteVerificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ ViewSet for verification logs (read only)"""
    queryset = VerificationLog.objects.all()
    serializer_class = SiteVerificationLogSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # filter logs for verifiers and super admins
    def get_queryset(self):

        user = self.request.user

        if user.is_verifier or user.is_superuser:
            return VerificationLog.objects.all()
        return VerificationLog.objects.filter(site__site_settings__verifiers=user).distinct()

    @action(detail=True, methods=['get'], url_path='verification-logs', url_name='verification-logs',
            permission_classes=[IsAuthenticated, IsVerifier])
    def verification_logs(self, request, pk=None):
        site_id = pk
        queryset = VerificationLog.objects.filter(
            site_id=site_id
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
