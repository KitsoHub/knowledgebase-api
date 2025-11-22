# heritage_sites/services.py
from django.db import transaction
from django.db.models import Count
from django.core.exceptions import PermissionDenied, ValidationError
# from django.core.mail import send_mail
# from django.conf import settings
from core.models import SiteVerificationVote, SiteSettings, VerificationLog


class VerificationService:
    """Service class handling verification business logic"""

    @staticmethod
    def process_vote(site, verifier, vote, comment=''):
        """
        Process a verification vote with validation.

        Args:
            site: Site instance
            verifier: User instance
            vote: 'approve' or 'reject'
            comment: Optional comment text

        Returns:
            Verification instance

        Raises:
            PermissionDenied: If user cannot verify
            ValidationError: If vote already exists
        """

        site_settings = SiteSettings.load()
        if verifier not in site_settings.verifiers.all():
            raise PermissionDenied("User is not authorized to verify sites")

        if SiteVerificationVote.objects.filter(site=site, verifier=verifier).exists():
            raise ValidationError("User has already voted on this site")

        if site.status != 'pending':
            raise ValidationError(f"Cannot vote on {site.status} site")

        with transaction.atomic():
            verification = SiteVerificationVote.objects.create(
                site=site,
                verifier=verifier,
                vote=vote,
                comment=comment
            )

        return verification

    @staticmethod
    def check_verification_threshold(instance):
        """
        Check current verification status without making changes.

        Returns:
            dict with vote counts and whether threshold is met
        """
        settings_obj = SiteSettings.load()
        required = settings_obj.required_verifier_count

        # verifications = site.site_verification_vote.all()
        # approve_count = verifications.filter(vote='approve').count()
        # reject_count = verifications.filter(vote='reject').count()
        site = instance.site
        previous_status = site.status
        new_status = None

        vote_counts = site.site_verification_vote.values(
            'vote').annotate(count=Count('vote'))
        approve_count = next(
            (item['count'] for item in vote_counts if item['vote'] == 'approve'), 0)
        reject_count = next(
            (item['count'] for item in vote_counts if item['vote'] == 'reject'), 0)

        if approve_count >= required:
            # site.status = 'verified'
            # site.save()
            new_status = 'verified'

        elif reject_count >= required:
            # site.status = 'rejected'
            # site.save()
            new_status = 'rejected'

        if new_status and new_status != previous_status:
            with transaction.atomic():
                site.status = new_status
                site.save()

                VerificationLog.objects.create(
                    site=site,
                    previous_status=previous_status,
                    new_status=new_status,
                    changed_by=instance.verifier,
                    is_override=False,
                    reason="Threshold reached"
                )

    @staticmethod
    @transaction.atomic
    def admin_override(site, new_status, admin_user, reason=''):
        """
        Allow admin to override verification status.

        Args:
            site: Site instance
            new_status: 'verified' or 'rejected'
            admin_user: User with override permission
            reason: Reason for override

        Returns:
            Updated site instance

        Raises:
            PermissionDenied: If user lacks override permission
            ValidationError: If invalid status
        """
        if not admin_user.has_perm('heritage_sites.can_override_verification'):
            raise PermissionDenied("User does not have override permission")

        if new_status not in ['verified', 'rejected']:
            raise ValidationError("Status must be 'verified' or 'rejected'")

        previous_status = site.status

        site.status = new_status
        site.save(update_fields=['status', 'last_updated'])
        VerificationLog.objects.create(
            site=site,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=admin_user,
            is_override=True,
            reason=reason or "Admin override"
        )

        # with transaction.atomic():
        #     site.status = new_status
        #     site.save(update_fields=['status', 'last_updated'])

        #     # Create audit log for override
        #     VerificationLog.objects.create(
        #         site=site,
        #         previous_status=previous_status,
        #         new_status=new_status,
        #         changed_by=admin_user,
        #         is_override=True,
        #         reason=reason or "Admin override"
        #     )

        # Send notifications
        # NotificationService.notify_status_change(
        #     site=site,
        #     old_status=previous_status,
        #     new_status=new_status,
        #     changed_by=admin_user,
        #     is_override=True
        # )
        site.site_verification_vote.all().delete()
        return site
