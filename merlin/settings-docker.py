from merlin.settings import *

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

STATIC_ROOT = '/var/webstack-data/django-static'
STATIC_URL = '/django-static/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME' : 'merlin',
        'USER' : 'postgres',
        'PASSWORD' : 'tuatara',
        'HOST' : 'the-postgres',
        'PORT' : '5432'
    }
}

