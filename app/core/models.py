from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin, AbstractUser
)
from django.conf import settings
from .managers import UserManager
from .choices import (
    DOCUMENT_TYPE, ONBOARDING_TYPE, STATUS_CHOICES, KNOWLEDGE_CATEGORY)
from .helpers import document_path, image_path


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
