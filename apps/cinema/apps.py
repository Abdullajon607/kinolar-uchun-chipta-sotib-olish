from django.apps import AppConfig


class CinemaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    # Package path under project root
    name = "apps.cinema"
    # Preserve migration history and DB app label
    label = "cinema"
