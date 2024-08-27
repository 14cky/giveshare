from django.apps import AppConfig
from django.dispatch import Signal

user_signed_up = Signal()

class GiveConfig(AppConfig):
    name = 'give'

    def ready(self):
        import give.signals  # Import signals
