from django.apps import AppConfig


class UserappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userApp'

def ready(self):
        # Or if signals are in models.py:
        from . import models