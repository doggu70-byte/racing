from django.apps import AppConfig


class RacingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.racing'
    verbose_name = '경마 관리'