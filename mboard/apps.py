from django.apps import AppConfig
import redis


class MboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mboard'


    def ready(self):
        import mboard.signals

red = redis.Redis(host = 'localhost', port = 6379)