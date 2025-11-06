from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin
)
from django.conf import settings
from .managers import UserManager
from .choices import (
    DOCUMENT_TYPE, KNOWLEDGE_CATEGORY,
    ONBOARDING_TYPE, SITES_CATEGORY_CHOICES,
    SITES_SENSITIVITY_LEVELS, STATUS_CHOICES, VOTE_CHOICES, SITES_STATUS_CHOICES)
from .helpers import document_path, image_path
from django.db.models import Count
from django.core.validators import MinValueValidator, MaxValueValidator


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


class Department(models.Model):
    dept_name = models.CharField(max_length=100)
    description = models.TextField()
    mission = models.TextField()
    goals = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.dept_name} Department'

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'


class Onboarding(models.Model):
    onboarding_name = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='department',
        null=True, blank=True)
    onboarding_type = models.CharField(
        max_length=50,
        choices=ONBOARDING_TYPE,
        default='test',
        help_text="Verification status",
    )
    notes = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Verification status",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.user.email} {self.status}'

    class Meta:
        verbose_name = 'OnboardingNote'
        verbose_name_plural = 'OnboardingNotes'


class OnboardingStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    VETTING = 'vetting', 'Vetting'
    VERIFIED = 'verified', 'Verified'
    PUBLISHED = 'published', 'Published'


class OnboardingNoteImages(models.Model):
    """Class representing onboarding images"""

    note = models.ForeignKey(
        Onboarding,
        related_name='images',
        on_delete=models.CASCADE,
        blank=True, null=True)
    images = models.ImageField(null=True, upload_to=image_path)

    def __str__(self) -> str:
        return self.note.onboarding_name

    class Meta:
        verbose_name = "Onboarding Notes Images"
        verbose_name_plural = "Onboarding Notes Images"


# TODO: add onboarding steps for a particular onaboarding
class OnboardingStep(models.Model):
    """Class for onboarding steps"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,)
    onboarding = models.ForeignKey(
        Onboarding, related_name='onboardingstep',
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    step_title = models.CharField(max_length=100)
    step_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.step_title}"


class OnboardingStepImages(models.Model):
    """Class representing onboarding images"""

    step = models.ForeignKey(
        OnboardingStep,
        related_name='images',
        on_delete=models.CASCADE,
        blank=True, null=True)
    images = models.ImageField(null=True, upload_to=image_path)

    def __str__(self) -> str:
        return self.step.step_title

    class Meta:
        verbose_name = "Onboarding Step Images"
        verbose_name_plural = "Onboarding Step Images"

# TODO: add policies


class Policy(models.Model):
    """Class representing policies"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    version = models.CharField(
        max_length=20, default='v1.0', blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='created_policies',
        null=True, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='policy_department',
        null=True, blank=True)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='approved_policies',
        null=True, blank=True)
    document_type = models.CharField(
        max_length=100,
        blank=True,
        choices=DOCUMENT_TYPE)
    document = models.FileField(upload_to=document_path,
                                null=True, blank=True)
    is_published = models.BooleanField(default=False)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Verification status",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.title} {self.document_type} {self.version}'

    class Meta:
        verbose_name = "Policies"
        verbose_name_plural = "Policies"


# TODO: add compliance
# TODO: add knowledge base
class KnowledgeBase(models.Model):
    """Class representing policies"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL
    )
    knowledge_title = models.CharField(max_length=200)
    content = models.TextField()
    version = models.CharField(
        max_length=20, default='v1.0', blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='created_knowledge',
        null=True, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='knowledge_department',
        null=True, blank=True)
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='verified_knowledge',
        null=True, blank=True)
    published_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='published_knowledge',
        null=True, blank=True)
    knowledge_category = models.CharField(
        max_length=100,
        blank=True,
        choices=KNOWLEDGE_CATEGORY, default='general')
    document_type = models.CharField(
        max_length=100,
        blank=True,
        choices=DOCUMENT_TYPE)
    document = models.FileField(upload_to=document_path,
                                null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Verification status",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.title} {self.document_type} {self.version}'

    class Meta:
        verbose_name = "Knowledge Base"
        verbose_name_plural = "Knowledge Base"


class SiteMetadata(models.Model):
    """Separate metadata model for better querying and validation"""

    unesco = models.BooleanField(default=False)
    undp = models.BooleanField(default=False)
    unicef = models.BooleanField(default=False)
    local_context = models.TextField(blank=True)
    indigenous_system = models.CharField(max_length=255, blank=True)
    rights = models.TextField(blank=True)
    ip_metadata = models.TextField(blank=True)
    sensitivity_level = models.CharField(
        max_length=20,
        choices=SITES_SENSITIVITY_LEVELS,
        default='public'
    )
    access_protocol = models.TextField(blank=True)


# Heritage Sites Model


class SiteSettings(models.Model):
    """Global settings for site verification system"""

    required_verifier_count = models.PositiveIntegerField(
        default=2,
        help_text="Number of verifier votes required to change status"
    )
    verifiers = models.ManyToManyField(
        User,
        related_name='verifier_settings',
        limit_choices_to={'groups__name': 'verifiers'},
        help_text="Users who can verify sites"
    )

    # Singleton pattern - only one settings instance
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"


class SiteQuerySet(models.QuerySet):
    """ Custom QuerySet for Heritage Sites """

    def pending(self):
        return self.filter(status='pending')

    def verified(self):
        return self.filter(status='verified')

    def rejected(self):
        return self.filter(status='rejected')

    def awaiting_verification(self):
        return self.filter(status='pending').annotate(
            vote_count=Count('site_verification_vote')
        ).filter(
            vote_count__lt=models.F(
                'site_settings__required_verifier_count'
            ))

    def by_category(self, category):
        return self.filter(category=category)

    def public_sites(self):
        return self.filter(sensitivity_level='public')


class SiteManager(models.Manager):
    """Custom manager for Site model"""

    def get_queryset(self):
        return SiteQuerySet(self.model, using=self._db)

    def pending(self):
        return self.get_queryset().pending()

    def verified(self):
        return self.get_queryset().verified()

    def rejected(self):
        return self.get_queryset().rejected()

    def awaiting_verification(self):
        return self.get_queryset().awaiting_verification()


class HeritageSite(models.Model):
    site_name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=SITES_STATUS_CHOICES,
        default='pending'
    )
    category = models.CharField(max_length=20, choices=SITES_CATEGORY_CHOICES)

    # TODO: For production GeoDjango: PointField, PolygonField, LineStringField
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )

    # TODO: add media field for images, videos, audio
    # TODO: add reference links field
    population_density = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    migration_route = models.TextField(blank=True, null=True)
    metadata = models.OneToOneField(
        SiteMetadata,
        on_delete=models.CASCADE,
        related_name='site_metadata',
    )
    site_settings = models.ForeignKey(
        SiteSettings,
        on_delete=models.PROTECT,
        default=1  # Default global settings
    )
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='created_site',
        null=True, blank=True)

    objects = SiteManager()

    def get_verification_status(self):

        votes = self.site_verification_vote.all().values(
            'vote').annotate(count=Count('vote'))
        vote_counts = {item['vote']: item['count'] for item in votes}
        return {
            'total_votes': self.site_verification_vote.count(),
            'required_votes': self.site_settings.required_verifier_count,
            'approve_count': vote_counts.get('approve', 0),
            'reject_count': vote_counts.get('reject', 0),
            'status': self.status
        }

    def can_user_verify(self, user):
        """Check if user can verify this site"""
        settings = SiteSettings.load()
        return (
            user in settings.verifiers.all() and
            not self.site_verification_vote.filter(verifier=user).exists()
        )

    class Meta:
        ordering = ['-date_created']
        indexes = [
            models.Index(fields=['status', 'category']),
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['-date_created']),
        ]
        permissions = [
            ("can_verify_site", "Can verify sites"),
            ("can_override_verification", "Can override verification status"),
        ]

    def __str__(self) -> str:
        return f"{self.site_name} ({self.get_category_display()}) - {self.get_status_display()}"


class SiteVerificationVote(models.Model):
    """ Track verifier votes on heritage sites """
    site = models.ForeignKey(
        HeritageSite,
        on_delete=models.CASCADE,
        related_name='site_verification_vote'
    )
    verifier = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='site_verifier'
    )
    vote = models.CharField(
        max_length=10,
        choices=VOTE_CHOICES,
    )
    voted_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('site', 'verifier')
        ordering = ['-voted_at']
        indexes = [
            models.Index(fields=['site', 'vote']),
        ]

    def __str__(self) -> str:
        return f"{self.verifier.email} - {self.vote} on {self.site.site_name}"


class VerificationLog(models.Model):
    """Audit log for status changes and admin overrides"""

    site = models.ForeignKey(
        HeritageSite,
        on_delete=models.CASCADE,
        related_name='verification_logs'
    )
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_override = models.BooleanField(default=False)
    reason = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        override_text = " (OVERRIDE)" if self.is_override else ""
        return f"{self.site.name}: {self.previous_status} → {self.new_status}{override_text}"
