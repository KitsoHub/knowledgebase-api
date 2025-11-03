"""
Django Command to set up roles
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    """Command to set up roles for artifacts"""
    help = 'Set up roles for artifacts'

    def handle(self, *args, **options):
        """Entry point for command"""

        artifact_permission_codenames = [
            "view_artifacts",
            "view_artifactimages",
            "change_artifacts",
        ]

        try:
            with transaction.atomic():
                self.setup_group_with_permissions(
                    'ArtifactPublisher', artifact_permission_codenames)
                self.stdout.write(
                    self.style.SUCCESS('Roles and permissions have been set up successfully!'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error setting up roles: {e}"))
            raise

    def setup_group_with_permissions(self, group_name: str, permission_codenames: list[str]) -> None:
        # create group
        group, created = Group.objects.get_or_create(name=group_name)

        permissions = Permission.objects.filter(
            codename__in=permission_codenames)
        if permissions.count() != len(permission_codenames):
            missing = set(permission_codenames) - \
                set(permissions.values_list("codename", flat=True))
            raise ValueError(f"Missing permissions: {missing}")

        group.permissions.set(permissions)

    def _get_permission(self, codename: str) -> Permission:
        """
        Helper method to retrieve a permission by codename.
        """
        try:
            return Permission.objects.get(codename=codename)
        except Permission.DoesNotExist:
            raise ObjectDoesNotExist(
                f"Permission with codename '{codename}' does not exist.")

        # create permission / view and understand permissions
        # view_artifact = Permission.objects.get(codename='view_artifacts')
        # view_artifact_imgs = Permission.objects.get(
        #     codename='view_artifactimages')
        # update_artifact = Permission.objects.get(codename='change_artifacts')

        # # add permissions to group
        # publisher.permissions.add(
        #     view_artifact, view_artifact_imgs, update_artifact)
