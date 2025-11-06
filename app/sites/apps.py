from django.apps import AppConfig


class SitesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sites'
    verbose_name = 'Heritage Sites'

    def ready(self):
        """Import signals when app is ready"""
        import sites.signals  # noqa: F401
