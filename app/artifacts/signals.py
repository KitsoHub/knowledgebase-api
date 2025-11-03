from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Artifacts, ArtifactStatusLog
from datetime import date

# Artifacts signals


@receiver(post_save, sender=Artifacts)
def update_artifact_verification_date(sender, instance, created, **kwargs):
    if created and instance.status == 'draft':
        # Initial stage for new artifacts
        # ArtifactStatusLog.objects.create(
        #     artifact=instance,
        #     new_status=instance.status,
        #     changed_by=instance.user,
        # )
        # if instance.contributor is None:

        #     instance.contributor = instance.user
        #     instance.save()
        return

    if instance.status == 'verified' and not instance.verification_date:
        instance.verification_date = date.today()
        instance.save()
