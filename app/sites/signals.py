from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from core.models import SiteVerificationVote, VerificationLog, SiteSettings
from sites.services import VerificationService


@receiver(post_save, sender=SiteVerificationVote)
def update_site_status(sender, instance, created, **kwargs):
    """Update site status when a new vote is added"""
    if created:
        # Only check verification threshold if status is still pending
        if instance.site.status == 'pending':
            VerificationService.check_verification_threshold(instance)


# @receiver(post_save, sender=SiteVerificationVote)
def check_verification_threshold(sender, instance, created, **kwargs):
    """
    Has site reached verification threshold after a vote is cast.

    Logic:
    1. Count approve and reject votes
    2. Compare counts against required_verifier_count
    3. Update site status if threshold met
    4. Create audit log entry
    """
    if not created:
        return  # Only process new votes

    site = instance.site
    settings = SiteSettings.load()
    required_count = settings.required_verifier_count

    verifications = site.site_verification_vote.all()
    approve_count = verifications.filter(vote='approve').count()
    reject_count = verifications.filter(vote='reject').count()

    previous_status = site.status
    new_status = None

    if approve_count >= required_count:
        new_status = 'verified'

    elif reject_count >= required_count:
        new_status = 'rejected'

    if new_status and new_status != previous_status:
        with transaction.atomic():
            site.status = new_status
            site.save(update_fields=['status', 'last_updated'])

            VerificationLog.objects.create(
                site=site,
                previous_status=previous_status,
                new_status=new_status,
                changed_by=instance.verifier,
                is_override=False,
                reason=f"Threshold reached: {approve_count} approvals, {reject_count} rejections"
            )

    else:
        pass
