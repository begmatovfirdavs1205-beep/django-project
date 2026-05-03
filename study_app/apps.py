from django.apps import AppConfig


class StudyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'study_app'
    verbose_name = 'AI Study Helper'

    def ready(self):
        import study_app.signals  # noqa: F401
