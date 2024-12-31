from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from .utils import create_default_profile_image
        create_default_profile_image()
        import accounts.signals
