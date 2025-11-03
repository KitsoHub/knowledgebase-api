from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
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


admin.site.register(models.Department)
admin.site.register(models.Onboarding)
admin.site.register(models.OnboardingNoteImages)
admin.site.register(models.OnboardingStep)
admin.site.register(models.Policy)
