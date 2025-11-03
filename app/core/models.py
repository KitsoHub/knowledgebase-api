from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin, AbstractUser
)
from django.conf import settings
from .managers import UserManager
from .choices import (
    ARTIFACT_TYPE, STATUS_CHOICES)
from .helpers import image_path


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User in the System"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_vetter = models.BooleanField(default=False)
    is_verifier = models.BooleanField(default=False)
    is_publisher = models.BooleanField(default=False)

    # unique identifier
    USERNAME_FIELD = 'email'

    # objects
    objects = UserManager()

    def __str__(self) -> str:
        return self.email

# Artifacts


class ArtifactStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    VETTING = 'vetting', 'Vetting'
    VERIFIED = 'verified', 'Verified'
    PUBLISHED = 'published', 'Published'


class Artifacts(models.Model):
    """Class representing artifacts"""

    artifact_name = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL
    )
    artifact_type = models.CharField(max_length=100, choices=ARTIFACT_TYPE)
    description = models.TextField(blank=True)
    historical_significance = models.PositiveIntegerField(
        default=1, blank=True, null=True)
    cultural_significance = models.PositiveIntegerField(
        default=1, blank=True, null=True)
    submission_date = models.DateField(auto_now_add=True)
    vetted_date = models.DateField(blank=True, null=True)
    verification_date = models.DateField(blank=True, null=True)
    vetted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='vetted_by', blank=True,
        null=True, on_delete=models.SET_NULL)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='verified_by', blank=True,
        null=True, on_delete=models.SET_NULL)
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='published_by', blank=True,
        null=True, on_delete=models.SET_NULL)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=ArtifactStatus.DRAFT,
        help_text="Verification status",
    )
    published_date = models.DateField(blank=True, null=True)

    def __str__(self) -> str:
        return self.artifact_name

    def save(self, *args, **kwargs):
        # add transition handler
        # initial_status = Artifacts.objects.get(pk=self.pk).status
        # if self.status == 'published' and initial_status == 'draft':
        #     raise ValueError(
        #         'Cannot transition directly from draft to published.')
        # Check if this is an update to an existing record
        if not self.pk:
            # New object: Create a log entry for the initial status
            if self.status == 'published':
                raise ValueError(
                    'Cannot transition directly from draft to published.')

            super().save(*args, **kwargs)  # Save the object to assign a primary key
            ArtifactStatusLog.objects.create(
                artifact=self,
                previous_status=None,
                new_status=self.status,
                changed_by=self.user,
            )
            return
        else:
            # Existing object: Validate status transitions
            old_status = Artifacts.objects.get(pk=self.pk).status
            changed_by = kwargs.pop('changed_by', None)

            # Log the status change if it actually changes
            if old_status != self.status:
                valid_transitions = {
                    ArtifactStatus.DRAFT: [ArtifactStatus.DRAFT,
                                           ArtifactStatus.VETTING],
                    ArtifactStatus.VETTING: [ArtifactStatus.VERIFIED],
                    ArtifactStatus.VERIFIED: [ArtifactStatus.PUBLISHED],
                    ArtifactStatus.PUBLISHED: [],
                }

            # Check if the new status is a valid transition
                if self.status not in valid_transitions.get(old_status, []):
                    raise ValueError(f"Invalid status transition from \
                        {old_status} to {self.status}.")
                if self.status == ArtifactStatus.VETTING:
                    changed_by = self.vetted_by
                elif self.status == ArtifactStatus.VERIFIED:
                    changed_by = self.verified_by
                elif self.status == ArtifactStatus.PUBLISHED:
                    changed_by = self.published_by

                ArtifactStatusLog.objects.create(
                    artifact=self,
                    previous_status=old_status,
                    new_status=self.status,
                    changed_by=changed_by,
                )
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Artifacts"
        verbose_name_plural = "Artifacts"

# add verifier registrations
# add publisher registrations


class ArtifactImages(models.Model):
    """Class representing artifact images"""

    artifact = models.ForeignKey(
        Artifacts,
        related_name='images',
        on_delete=models.CASCADE,
        blank=True, null=True)
    images = models.ImageField(null=True, upload_to=image_path)

    def __str__(self) -> str:
        return self.artifact.artifact_name

    class Meta:
        verbose_name = "Artifact Images"
        verbose_name_plural = "Artifact Images"

# Artifact status log


class ArtifactStatusLog(models.Model):
    artifact = models.ForeignKey(
        'Artifacts', on_delete=models.CASCADE, related_name='status_logs')
    previous_status = models.CharField(
        max_length=50, choices=ArtifactStatus.choices, null=True)
    new_status = models.CharField(
        max_length=50, choices=ArtifactStatus.choices)
    changed_by = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:

        return f"{self.artifact.artifact_name}: \
            {self.previous_status} -> {self.new_status}"

    class Meta:
        verbose_name = "Artifact Status Log"
        verbose_name_plural = "Artifact Status Log"
