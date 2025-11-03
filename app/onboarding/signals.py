from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Onboarding

# Onboarding signals

@receiver(post_save, sender=Onboarding)
def update_onboarding_verification_date(sender, instance, created, **kwargs):
    if created and instance.status == 'draft':

        return
