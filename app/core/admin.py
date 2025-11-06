from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from core import models


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    """User Admin"""

    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {
            "fields": (
                'email', 'password'
            ),
        }),
        (_('Personal Info'), {'fields': ('name',)}),
        (_('Permissions'), {
         'fields': ('is_active', 'is_staff', 'is_verifier',
                    'is_vetter',
                    'is_publisher', 'is_superuser', 'groups')}),
        (_('Important dates'), {'fields': ('last_login',)})
    )

    add_fieldsets = (
        (None, {'classes': ('wide',),
                'fields': ('email',
                           'password1',
                           'password2',
                           'name',
                           'is_active',
                           'is_staff',
                           'is_verifier',
                           'is_vetter',
                           'is_publisher',
                           'is_superuser')}),
    )

    readonly_fields = ['last_login']


@admin.register(models.SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Admin for global site settings"""
    list_display = ['required_verifier_count', 'verifier_count']
    filter_horizontal = ['verifiers']

    def verifier_count(self, obj):
        return obj.verifiers.count()
    verifier_count.short_description = 'Number of Verifiers'

    def has_add_permission(self, request):
        # Only one settings instance allowed
        return not models.SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Cannot delete settings
        return False


class VerificationInline(admin.TabularInline):
    """Inline for verifications"""
    model = models.SiteVerificationVote
    extra = 0
    readonly_fields = ['verifier', 'vote', 'comment', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


class MetadataInline(admin.TabularInline):
    """Inline for verifications"""
    model = models.SiteMetadata
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


@admin.register(models.SiteVerificationVote)
class VerificationAdmin(admin.ModelAdmin):
    """Admin for verifications"""
    list_display = ['site', 'verifier', 'vote_badge', 'created_at']
    list_filter = ['vote', 'created_at']
    search_fields = ['site__name', 'verifier__username']
    readonly_fields = ['site', 'verifier', 'vote', 'comment', 'created_at']

    def vote_badge(self, obj):
        """Display vote with color"""
        color = 'green' if obj.vote == 'approve' else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_vote_display()
        )
    vote_badge.short_description = 'Vote'

    def has_add_permission(self, request):
        # Verifications should be created via API
        return False

    def has_delete_permission(self, request, obj=None):
        # Cannot delete verifications (audit trail)
        return False


@admin.register(models.VerificationLog)
class VerificationLogAdmin(admin.ModelAdmin):
    """Admin for verification logs"""
    list_display = [
        'site', 'previous_status', 'new_status',
        'changed_by', 'override_badge', 'timestamp'
    ]
    list_filter = ['is_override', 'timestamp', 'new_status']
    search_fields = ['site__name', 'changed_by__username']
    readonly_fields = [
        'site', 'previous_status', 'new_status',
        'changed_by', 'is_override', 'reason', 'timestamp'
    ]

    def override_badge(self, obj):
        """Display override status"""
        if obj.is_override:
            return format_html(
                '<span style="background: orange; color: white; padding: 2px 8px; '
                'border-radius: 3px;">OVERRIDE</span>'
            )
        return '-'
    override_badge.short_description = 'Override'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        # Cannot delete audit logs
        return False


@admin.register(models.HeritageSite)
class SiteAdmin(admin.ModelAdmin):
    """Admin for heritage sites"""
    list_display = [
        'site_name', 'category', 'status_badge', 'created_by', 'date_created'
    ]
    list_filter = ['status', 'category',
                   'metadata__sensitivity_level', 'date_created']
    search_fields = ['site_name', 'description', 'created_by__username']
    readonly_fields = ['date_created', 'last_updated',
                       'verification_summary', 'metadata_details']

    fieldsets = (
        ('Basic Information', {
            'fields': ('site_name', 'description', 'category', 'status')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'population_density', 'migration_route')
        }),
        ('Metadata', {
            'fields': ('metadata_details',),
            'classes': ('collapse',)
        }),
        ('Ownership & Dates', {
            'fields': ('created_by', 'date_created', 'last_updated'),
            'classes': ('collapse',)
        }),
        ('Verification', {
            'fields': ('verification_summary',)

        })
    )

    inlines = [VerificationInline]

    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'pending': 'orange',
            'verified': 'green',
            'rejected': 'red'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def verification_progress(self, obj):
        """Show verification progress"""
        status = obj.get_verification_status()
        html = f"""
        <div style="background: #f0f0f0; padding: 10px; border-radius: 5px;">
            <p><strong>Approvals:</strong> {status['approve_count']}/{status['required_count']}  approvals</p>
        </div>
        """
        return format_html(html)
    verification_progress.short_description = 'Verification'

    def verification_summary(self, obj):
        """Display detailed verification status"""
        if not obj.pk:
            return "Save site to see verification status"

        status = obj.get_verification_status()
        pending = status.get('pending_verifiers', 0)
        html = f"""
        <div style=" padding: 10px; border-radius: 5px;">
            <p><strong>Approvals:</strong> {status['approve_count']}/{status['required_count']}  approvals</p>
            <p><strong>Approvals:</strong> {status['approve_count']}</p>
            <p><strong>Rejections:</strong> {status['reject_count']}</p>
            <p><strong>Total Votes:</strong> {status['total_votes']}</p>
            <p><strong>Required:</strong> {status['required_count']}</p>
            <p></br><strong>Pending Verifiers:</strong> {pending}</p>
        </div>
        """
        return format_html(html)
    verification_summary.short_description = 'Verification Summary'

    def metadata_details(self, obj):
        if hasattr(obj, 'metadata'):
            return format_html(
                "<div><strong>UNESCO:</strong> {}<br/>"
                "<strong>Sensitivity:</strong> {}</div>",
                "Yes" if obj.metadata.unesco else "No",
                obj.metadata.get_sensitivity_level_display()
            )
        return "No metadata available"

    metadata_details.short_description = 'Metadata'


admin.site.register(models.Department)
admin.site.register(models.Onboarding)
admin.site.register(models.OnboardingNoteImages)
admin.site.register(models.OnboardingStep)
admin.site.register(models.Policy)
