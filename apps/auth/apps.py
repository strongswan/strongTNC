from django.apps import AppConfig


class AuthConfig(AppConfig):
    name = 'apps.auth'
    # avoid conflicts with django.contrib.auth
    label = 'extauth'
