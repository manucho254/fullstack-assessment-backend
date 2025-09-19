from .base import *

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),  # Or the IP address/hostname of your PostgreSQL server
        "PORT": env("DB_PORT"),  # Default PostgreSQL port
    }
}
