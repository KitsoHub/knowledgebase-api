from rest_framework import permissions
from core.models import SiteSettings


class IsVerifier(permissions.BasePermission):
    """
    Custom permission to only allow designated verifiers to verify sites.
    """

    message = "You must be a designated verifier to perform this action."

    def has_permission(self, request, view):

        if not (request.user.is_authenticated and request.user.is_verifier):
            return False

        settings = SiteSettings.load()
        return request.user in settings.verifiers.all()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners to edit their sites.
    Read permissions are allowed to any request.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions allowed for any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Staff can edit anything
        if request.user.is_staff:
            return True

        # Write permissions only to owner
        return obj.created_by == request.user


class CanOverrideVerification(permissions.BasePermission):
    """
    Permission for admin users to override verification status.
    """

    message = "You do not have permission to override verification status."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return request.user.has_perm('heritage_sites.can_override_verification')
